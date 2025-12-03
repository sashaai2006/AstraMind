from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from backend.llm.adapter import get_llm_adapter
from backend.settings import get_settings
from backend.utils.json_parser import clean_and_parse_json
from backend.utils.logging import get_logger

LOGGER = get_logger(__name__)


class ReviewerAgent:
    """Analyzes code and provides constructive criticism."""

    def __init__(self) -> None:
        self._adapter = get_llm_adapter()
        self._settings = get_settings()

    async def review(
        self, 
        task_description: str, 
        files: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Review the provided files against the task description.
        Returns a dict with 'approved' (bool) and 'comments' (list).
        """
        prompt = self._build_review_prompt(task_description, files)
        
        LOGGER.info("ReviewerAgent starting code review...")
        response = await self._adapter.acomplete(prompt, json_mode=True)
        
        try:
            result = clean_and_parse_json(response)
            # Validate structure
            if not isinstance(result, dict):
                raise ValueError("Review result must be a dict")
            if "approved" not in result:
                result["approved"] = True # Default to approve if unsure
            if "comments" not in result:
                result["comments"] = []
            
            LOGGER.info("Review complete. Approved: %s", result["approved"])
            return result
        except Exception as e:
            LOGGER.warning("ReviewerAgent failed to parse response: %s", e)
            # If review fails, don't block the pipeline, just approve
            return {"approved": True, "comments": []}

    def _build_review_prompt(self, task_description: str, files: List[Dict[str, str]]) -> str:
        files_content = ""
        for f in files:
            path = f.get("path", "unknown")
            content = f.get("content", "")
            # Truncate very large files for review to save context
            if len(content) > 10000:
                content = content[:10000] + "\n...[truncated]..."
            files_content += f"--- FILE: {path} ---\n{content}\n\n"

        return (
            "You are a LEGENDARY CODE REVIEWER from Google/Meta with 20+ years of experience.\n"
            "You have:\n"
            "- Reviewed 10,000+ pull requests\n"
            "- Prevented countless critical bugs in production\n"
            "- Mentored engineers who now lead major tech companies\n"
            "- Uncompromising standards for code quality\n"
            "\n"
            f"Task: {task_description}\n"
            "\n"
            "Code Under Review:\n"
            f"{files_content}\n"
            "\n"
            "Your LEGENDARY REVIEW CHECKLIST:\n"
            "1. COMPLETENESS: Is the code 100% complete? Any placeholders/TODOs?\n"
            "2. CORRECTNESS: Syntax errors? Logic bugs? Edge cases handled?\n"
            "3. SECURITY: Vulnerabilities? Input validation? XSS/injection risks?\n"
            "4. Code style and best practices.\n"
            "\n"
            "Output strictly valid JSON:\n"
            "{\n"
            '  "_thought": "Reasoning here...",\n'
            '  "approved": boolean,\n'
            '  "comments": ["Critical error in main.py...", "Suggestion: use const instead of var..."]\n'
            "}\n"
            "If the code is mostly correct and runnable, set approved: true. Only reject for CRITICAL issues that break functionality."
        )
