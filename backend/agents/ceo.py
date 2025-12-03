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
            "You are a technical CEO planning an MVP project. Your goal is to architect a scalable system.\n"
            f"Project description: {description}\n"
            f"Target platform: {target}\n"
            "\n"
            "Create a JSON execution plan. Break the project into independent parallel tracks where possible (e.g., 'frontend', 'backend', 'database').\n"
            "Output a JSON object with the following structure:\n"
            "{\n"
            '  "_thought": "Explain your reasoning for the plan and parallelization strategy...",\n'
            '  "steps": [\n'
            '    {\n'
            '      "name": "string (e.g. \'scaffold_frontend\', \'setup_database\')",'
            '      "agent": "developer",'
            '      "parallel_group": "string or null (steps with same group run in parallel)",'
            '      "payload": { "files": [ { "path": "path/to/file", "content": "DETAILED INSTRUCTIONS..." } ] }\n'
            '    }\n'
            '  ]\n'
            "}\n"
            "\n"
            "RULES:\n"
            "1. MAXIMIZE PARALLELISM: Put frontend and backend tasks in the same 'parallel_group' (e.g., 'phase_1').\n"
            "2. DETAILED SPECS: In 'payload.files.content', write DETAILED natural language instructions. Do NOT write code.\n"
            "3. Return ONLY valid JSON. No markdown formatting."
        )
        adapter = get_llm_adapter()
        try:
            LOGGER.info("CEO requesting plan from LLM...")
            response = await adapter.acomplete(prompt, json_mode=True)
            LOGGER.info("CEO received plan (len=%d)", len(response))
            
            # Parse response
            data = json.loads(response)
            
            # Handle Thought Streaming if present
            if "_thought" in data:
                # Ideally we would broadcast this, but CEO doesn't have WS manager context yet.
                # We'll log it for now.
                LOGGER.info("CEO Thought: %s", data["_thought"])
                
            steps = data.get("steps", [])
            if isinstance(data, list): # Fallback if LLM returned list directly
                steps = data

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
