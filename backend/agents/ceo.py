from __future__ import annotations

import json
from typing import Any, Dict, List
from uuid import uuid4

from backend.llm.adapter import get_llm_adapter
from backend.settings import get_settings
from backend.utils.logging import get_logger

LOGGER = get_logger(__name__)


class CEOAgent:
    """Generates a lightweight DAG describing required build steps."""

    async def plan(self, description: str, target: str) -> List[Dict[str, Any]]:
        settings = get_settings()
        if settings.llm_mode == "mock":
            return self._mock_plan(description, target)
        return await self._llm_plan(description, target)

    async def _llm_plan(self, description: str, target: str) -> List[Dict[str, Any]]:
        prompt = (
            "You are a technical CEO planning an MVP project.\n"
            f"Project description: {description}\n"
            f"Target platform: {target}\n"
            "Create a JSON plan consisting of a list of steps. Each step must have:\n"
            '- "name": string (e.g. "scaffold_frontend")\n'
            '- "agent": "developer"\n'
            '- "parallel_group": string or null (steps with same group run in parallel)\n'
            '- "payload": { "files": [ { "path": "path/to/file", "content": "DETAILED INSTRUCTIONS for developer on how to implement this file..." } ] }\n'
            "\n"
            "CRITICAL: In the 'content' field of 'payload', do NOT write code. Write DETAILED instructions in natural language explaining what logic the developer agent should implement in that file. This ensures that if the developer fails, we at least have the spec.\n"
            "\n"
            "Return ONLY valid JSON list of steps. Do not include markdown code blocks."
        )
        adapter = get_llm_adapter()
        try:
            LOGGER.info("CEO requesting plan from LLM...")
            response = await adapter.acomplete(prompt)
            LOGGER.info("CEO received plan (len=%d)", len(response))
            # Simple cleanup if LLM wraps in markdown
            cleaned = response.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            steps = json.loads(cleaned)
            # Ensure IDs
            for step in steps:
                if "id" not in step:
                    step["id"] = str(uuid4())
            return steps
        except Exception as exc:
            LOGGER.error("CEO plan generation failed: %s", exc)
            return self._mock_plan(description, target)

    def _mock_plan(self, description: str, target: str) -> List[Dict[str, Any]]:
        base_payload = [
            {
                "path": "README.md",
                "content": f"# {description}\n\nGenerated for target {target}.",
            },
            {
                "path": "src/main.py",
                "content": 'print("Hello from generated project")',
            },
        ]
        return [
            {
                "id": str(uuid4()),
                "name": "generate_frontend",
                "agent": "developer",
                "parallel_group": "build",
                "payload": {"files": base_payload},
            },
            {
                "id": str(uuid4()),
                "name": "generate_backend",
                "agent": "developer",
                "parallel_group": "build",
                "payload": {"files": base_payload},
            },
            {
                "id": str(uuid4()),
                "name": "package",
                "agent": "developer",
                "parallel_group": None,
                "payload": {
                    "files": [
                        {
                            "path": "manifest.json",
                            "content": json.dumps(
                                {"summary": description, "target": target}, indent=2
                            ),
                        }
                    ]
                },
            },
        ]
