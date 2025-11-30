from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID

from pathlib import Path

from backend.core.ws_manager import ws_manager
from backend.llm.adapter import get_llm_adapter
from backend.memory import utils as db_utils
from backend.memory.db import get_session
from backend.settings import get_settings
from backend.utils.fileutils import write_files
from backend.utils.json_parser import clean_and_parse_json
from backend.utils.logging import get_logger

LOGGER = get_logger(__name__)


class DeveloperAgent:
    """Transforms LLM JSON instructions into tangible project files."""

    def __init__(self, llm_semaphore) -> None:
        self._adapter = get_llm_adapter()
        self._settings = get_settings()
        self._semaphore = llm_semaphore

    async def _broadcast_thought(self, project_id: str, msg: str, level: str = "info"):
        """Helper to broadcast agent thoughts to the UI."""
        await ws_manager.broadcast(
            project_id,
            {
                "type": "event",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "project_id": project_id,
                "agent": "developer",
                "level": level,
                "msg": msg,
            },
        )

    async def run(
        self,
        step: Dict[str, Any],
        context: Dict[str, Any],
        stop_event,
    ) -> None:
        project_id = context["project_id"]
        if stop_event.is_set():
            LOGGER.info("Project %s stop requested; skipping step.", project_id)
            return

        payload = step.get("payload", {})
        files_spec = payload.get("files", [])
        
        await self._broadcast_thought(project_id, f"Analying specs for step: {step.get('name')}...")

        # Initial prompt
        prompt = self._build_prompt(context, step, files_spec)

        await self._broadcast_thought(project_id, "Generating code with LLM...")
        parsed_response = await self._execute_with_retry(prompt, step, context)

        # Fallback to empty files only if absolutely necessary
        file_defs = parsed_response.get("files") if parsed_response else []
        file_defs = self._normalize_files(file_defs, project_id)
        
        if not file_defs:
             # Try to fallback to specs if available, but this is usually just instructions
             # Better to save a placeholder saying it failed
             LOGGER.warning("DeveloperAgent failed to generate files for step %s. Saving failure artifacts.", step.get("name"))
             await self._broadcast_thought(project_id, "Failed to generate valid code. Saving error stubs.", "error")
             file_defs = []
             for spec in files_spec:
                 file_defs.append({
                     "path": spec.get("path", "unknown_artifact.txt"),
                     "content": f"// Failed to generate content for {spec.get('path')}.\n// Please check logs."
                 })

        project_path = self._settings.projects_root / project_id
        project_path.mkdir(parents=True, exist_ok=True)
        project_root = project_path.resolve()
        
        await self._broadcast_thought(project_id, f"Writing {len(file_defs)} files to disk...")
        saved = write_files(project_path, file_defs)
        relative_paths = [s.relative_to(project_root).as_posix() for s in saved]
        sizes = [s.stat().st_size for s in saved]

        async with get_session() as session:
            await db_utils.add_artifacts(
                session, UUID(project_id), relative_paths, sizes
            )

        for rel_path in relative_paths:
            await ws_manager.broadcast(
                project_id,
                {
                    "type": "event",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "project_id": project_id,
                    "agent": step.get("agent", "developer"),
                    "level": "info",
                    "msg": f"Artifact saved: {rel_path}",
                    "artifact_path": rel_path,
                },
            )
        await self._broadcast_thought(project_id, f"Step '{step.get('name')}' completed successfully.")

    async def _execute_with_retry(self, prompt: str, step: Dict[str, Any], context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Execute LLM call with retries and repair logic."""
        max_retries = 2
        current_prompt = prompt
        project_id = context["project_id"]
        
        for attempt in range(max_retries + 1):
            LOGGER.info(
                "Calling LLM adapter (mode=%s) for step %s (attempt %d/%d)",
                self._settings.llm_mode,
                step.get("name"),
                attempt + 1,
                max_retries + 1
            )
            
            if attempt > 0:
                await self._broadcast_thought(project_id, f"Retrying LLM generation (attempt {attempt + 1}/{max_retries + 1})...", "warning")

            async with self._semaphore:
                # Use JSON mode for native structure enforcement
                completion = await self._adapter.acomplete(current_prompt, json_mode=True)
            
            LOGGER.info("LLM response received (length=%d)", len(completion))
            
            try:
                parsed = clean_and_parse_json(completion)
                if isinstance(parsed, dict) and "files" in parsed:
                    # Log reasoning if present
                    if "_thought" in parsed:
                        await self._broadcast_thought(project_id, f"Developer thought: {parsed['_thought']}", "info")
                    return parsed
                elif isinstance(parsed, list):
                    # Handle case where LLM returns list of files directly
                    return {"files": parsed}
                else:
                    raise ValueError("JSON is valid but does not contain 'files' or is not a list")
            except Exception as exc:
                LOGGER.warning("JSON parse failed on attempt %d: %s", attempt + 1, exc)
                if attempt < max_retries:
                    await self._broadcast_thought(project_id, "Received invalid JSON from LLM. Attempting auto-repair...", "warning")
                    # Update prompt to ask for repair
                    current_prompt = (
                        "The previous response was invalid JSON. Please fix it.\n"
                        f"Error: {exc}\n"
                        "Return ONLY valid JSON with 'files' array.\n"
                        "Previous response was:\n"
                        f"{completion[:2000]}" # Limit context
                    )
                    continue
        
        return None

    def _build_prompt(
        self, context: Dict[str, Any], step: Dict[str, Any], files_spec: List[Dict[str, Any]]
    ) -> str:
        spec = json.dumps(files_spec, indent=2)
        return (
            "You are a senior software developer.\n"
            f"Project: {context['title']} ({context['target']})\n"
            f"Description: {context['description']}\n"
            f"Task: Implement the files for step '{step.get('name')}'.\n"
            "\n"
            "Below is the file specification (paths and instructions). "
            "You must REPLACE the 'content' with actual, working, production-quality code based on the instructions.\n"
            f"FILES_SPEC::{spec}\n"
            "\n"
            "Output ONLY valid JSON. The format must be strictly:\n"
            "{\n"
            '  "_thought": "Step-by-step plan...",\n'
            '  "files": [ { "path": "...", "content": "..." } ]\n'
            "}\n"
            "IMPORTANT: Do not include any explanations, markdown formatting, or code blocks (like ```json). Just the raw JSON string.\n"
            "WARNING: Ensure all strings are properly escaped. Do not use triple quotes inside JSON."
        )

    def _normalize_files(
        self, file_defs: Optional[List[Dict[str, Any]]], project_id: str
    ) -> List[Dict[str, str]]:
        if not file_defs:
            return []

        normalized: List[Dict[str, str]] = []

        for file in file_defs:
            path_value = file.get("path")
            content_value = file.get("content", "")

            if not path_value or not isinstance(path_value, str):
                LOGGER.warning("DeveloperAgent skipping file without valid path: %s", file)
                continue

            safe_path = path_value.strip()
            if not safe_path or ".." in Path(safe_path).parts:
                LOGGER.warning("DeveloperAgent skipping unsafe path: %s", path_value)
                continue

            if isinstance(content_value, (dict, list)):
                content_str = json.dumps(content_value, indent=2)
            else:
                content_str = str(content_value)

            normalized.append({"path": safe_path, "content": content_str})

        return normalized
