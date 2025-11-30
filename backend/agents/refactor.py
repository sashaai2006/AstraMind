from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import UUID

from backend.core.ws_manager import ws_manager
from backend.llm.adapter import get_llm_adapter
from backend.memory import utils as db_utils
from backend.memory.db import get_session
from backend.settings import get_settings
from backend.utils.fileutils import write_files, iter_file_entries, read_project_file
from backend.utils.json_parser import clean_and_parse_json
from backend.utils.logging import get_logger

LOGGER = get_logger(__name__)


class RefactorAgent:
    """Agent that refactors or creates files based on user chat messages."""

    def __init__(self) -> None:
        self._adapter = get_llm_adapter()
        self._settings = get_settings()

    async def _broadcast_thought(self, project_id: str, msg: str, level: str = "info"):
        """Helper to broadcast agent thoughts to the UI."""
        await ws_manager.broadcast(
            project_id,
            {
                "type": "event",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "project_id": project_id,
                "agent": "refactor",
                "level": level,
                "msg": msg,
            },
        )

    async def chat(self, project_id: UUID, message: str, history: Optional[List[Dict[str, str]]] = None) -> str:
        project_path = self._settings.projects_root / str(project_id)
        if not project_path.exists():
            return "Project not found."

        context_files = self._read_context_files(project_path, user_query=message)
        await self._broadcast_thought(str(project_id), "Reading context files...")
        
        prompt = self._build_chat_prompt(message, context_files, history or [])

        LOGGER.info("RefactorAgent calling LLM for project %s", project_id)
        await self._broadcast_thought(str(project_id), "Thinking about your request...")
        
        # Use native JSON mode if available
        response = await self._adapter.acomplete(prompt, json_mode=True)
        
        LOGGER.info("RefactorAgent raw response length: %d", len(response))
        # Log first 500 chars to see start of response
        LOGGER.info("RefactorAgent raw response start: %s", response[:500])

        try:
            updates = clean_and_parse_json(response)
            if not isinstance(updates, dict):
                raise ValueError("Parsed JSON is not a dictionary")
        except Exception as exc:
            LOGGER.error("Failed to parse RefactorAgent response: %s. Raw start: %s", exc, response[:500])
            await self._broadcast_thought(str(project_id), f"Failed to parse LLM response: {exc}", "error")
            return f"I failed to process the request. The LLM response was invalid JSON. Error: {exc}. Please try again."

        # Log thought if present (Chain-of-Thought)
        if "_thought" in updates:
            thought = updates["_thought"]
            await self._broadcast_thought(str(project_id), f"Thought: {thought}", "info")

        files_to_update = self._normalize_files(updates.get("files"))
        response_message = updates.get("message", "Done.")

        if not files_to_update:
            LOGGER.warning("RefactorAgent returned no files to update. Message: %s", response_message)
            await self._broadcast_thought(str(project_id), "No file changes proposed.", "warning")
        
        if files_to_update:
            try:
                await self._broadcast_thought(str(project_id), f"Applying changes to {len(files_to_update)} files...")
                saved = write_files(project_path, files_to_update)
                # Update artifacts in DB
                sizes = [s.stat().st_size for s in saved]
                relative_paths = [s.relative_to(project_path).as_posix() for s in saved]
                
                async with get_session() as session:
                    await db_utils.add_artifacts(
                        session, project_id, relative_paths, sizes
                    )
                    await db_utils.record_event(
                        session,
                        project_id,
                        f"Refactor applied: {len(saved)} files changed",
                        agent="refactor",
                    )

                # Notify frontend
                for rel_path in relative_paths:
                    await ws_manager.broadcast(
                        str(project_id),
                        {
                            "type": "event",
                            "timestamp": "",
                            "project_id": str(project_id),
                            "agent": "refactor",
                            "level": "info",
                            "msg": f"Updated {rel_path}",
                            "artifact_path": rel_path,
                        },
                    )
                
                if "modified" not in response_message.lower() and "created" not in response_message.lower():
                    response_message += f"\n(Updated {len(saved)} files)"
            
            except Exception as e:
                LOGGER.error("Failed to write files: %s", e)
                await self._broadcast_thought(str(project_id), f"Error writing files: {e}", "error")
                return f"Error writing files: {e}"

        return response_message

    def _read_context_files(self, project_path: Path, user_query: str = "") -> str:
        """Read text files to provide context to LLM with smart selection."""
        entries = iter_file_entries(project_path)
        
        # Scoring function
        def score_entry(entry):
            score = 0
            path_str = entry.path.lower()
            query_terms = user_query.lower().split()
            
            # Match terms in query
            for term in query_terms:
                if len(term) > 3 and term in path_str:
                    score += 10
            
            # Prioritize source code
            if path_str.endswith(('.py', '.tsx', '.ts', '.js', '.html', '.css')):
                score += 5
            elif path_str.endswith('.json') or path_str.endswith('.md'):
                score += 2
            else:
                score -= 5 # Lockfiles, maps, etc.
                
            # Penalty for size
            if entry.size_bytes > 10000:
                score -= 2
            if entry.size_bytes > 50000:
                score -= 10
                
            return score

        # Sort by score descending
        sorted_entries = sorted(entries, key=score_entry, reverse=True)
        
        buffer = []
        total_chars = 0
        MAX_CHARS = 25000 # Approximate limit for context window

        for entry in sorted_entries:
            if entry.is_dir:
                continue
            
            # Hard skip very large files
            if entry.size_bytes > 100000:
                continue
            
            try:
                content, is_text = read_project_file(project_path, entry.path)
                if is_text:
                    text = content.decode("utf-8")
                    
                    # Skip map files and lock files content unless explicitly asked
                    if ("lock" in entry.path or entry.path.endswith(".map")) and score_entry(entry) < 5:
                        buffer.append(f"--- FILE: {entry.path} (skipped content) ---")
                        continue

                    if total_chars + len(text) > MAX_CHARS:
                        buffer.append(f"--- FILE: {entry.path} (truncated) ---\n[Content skipped due to size limit]")
                    else:
                        buffer.append(f"--- FILE: {entry.path} ---\n{text}")
                        total_chars += len(text)
            except Exception:
                pass
        
        return "\n\n".join(buffer)

    def _build_chat_prompt(self, user_message: str, context_files: str, history: List[Dict[str, str]]) -> str:
        history_text = ""
        if history:
            history_text = "Conversation History:\n"
            for msg in history[-5:]: # Limit to last 5 messages to save tokens
                role = msg.get("role", "unknown")
                content = msg.get("content", "")
                history_text += f"- {role}: {content}\n"
            history_text += "\n"

        return (
            "You are an expert software developer AI. You modify project files to fulfill user requests.\n"
            "Below are the current project files:\n"
            f"{context_files}\n"
            "\n"
            f"{history_text}"
            "User Request:\n"
            f"{user_message}\n"
            "\n"
            "CRITICAL INSTRUCTIONS:\n"
            "1. First, THINK about the changes needed. Put your reasoning in the '_thought' field.\n"
            "2. You MUST return the FULL content of the modified/new files in the 'files' array.\n"
            "3. Return ONLY a valid JSON object. No markdown code blocks.\n"
            "4. IMPORTANT: For JSON string values, use ONLY double quotes (\"). Do NOT use backticks (`) or single quotes (').\n"
            "5. CRITICAL: If you write code (like JavaScript or GLSL shaders) inside the JSON 'content' string, you MUST escape all newlines as \\n. \n"
            "   Example INCORRECT: \"content\": \"var x = 1;\nvar y = 2;\"\n"
            "   Example CORRECT: \"content\": \"var x = 1;\\nvar y = 2;\"\n"
            "6. Structure:\n"
            "{\n"
            '  "_thought": "The user wants X. I will modify Y to do Z...",\n'
            '  "message": "Description...",\n'
            '  "files": [\n'
            '    { "path": "public/index.html", "content": "<!DOCTYPE html>\\n<html>..." }\n'
            '  ]\n'
            "}\n"
        )

    def _normalize_files(self, files: Optional[List[Dict[str, Any]]]) -> List[Dict[str, str]]:
        if not files:
            return []

        normalized: List[Dict[str, str]] = []
        for file in files:
            path_value = file.get("path")
            content_value = file.get("content", "")

            if not path_value or not isinstance(path_value, str):
                LOGGER.warning("RefactorAgent skipping file without valid path: %s", file)
                continue

            safe_path = path_value.strip()
            if not safe_path or ".." in Path(safe_path).parts:
                LOGGER.warning("RefactorAgent skipping unsafe path: %s", path_value)
                continue

            if isinstance(content_value, (dict, list)):
                content_str = json.dumps(content_value, indent=2)
            else:
                content_str = str(content_value)

            normalized.append({"path": safe_path, "content": content_str})

        return normalized
