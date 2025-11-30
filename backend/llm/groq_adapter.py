from __future__ import annotations

import os
from typing import Optional

import logging
from groq import AsyncGroq, RateLimitError, APIError, BadRequestError
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)

from backend.utils.logging import get_logger

from .adapter import BaseLLMAdapter

LOGGER = get_logger(__name__)


class GroqLLMAdapter(BaseLLMAdapter):
    """Adapter for Groq API (fast inference)."""

    def __init__(self, model: str = "llama-3.1-8b-instant"):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            LOGGER.warning("GROQ_API_KEY not found. Groq adapter will fail.")
        self.client = AsyncGroq(api_key=api_key)
        self.model = model

    @retry(
        retry=retry_if_exception_type((RateLimitError, APIError, ConnectionError)),
        wait=wait_exponential(multiplier=1, min=2, max=20),
        stop=stop_after_attempt(5),
        before_sleep=before_sleep_log(LOGGER, logging.INFO),
    )
    async def acomplete(self, prompt: str, json_mode: bool = False) -> str:
        try:
            return await self._invoke(prompt, json_mode=json_mode)
        except BadRequestError as exc:
            LOGGER.error("Groq bad request (json_mode=%s): %s", json_mode, exc)
            if json_mode:
                LOGGER.warning("Falling back to text mode (json_mode=False) due to bad request.")
                return await self._invoke(prompt, json_mode=False)
            raise
        except Exception as exc:
            LOGGER.error("Groq request failed: %s", exc)
            raise

    async def _invoke(self, prompt: str, json_mode: bool) -> str:
        LOGGER.info("Calling Groq with model '%s' (json_mode=%s)", self.model, json_mode)
        response_format = {"type": "json_object"} if json_mode else None
        system_prompt = "You are a helpful assistant."
        if json_mode:
            system_prompt += " You MUST output valid JSON."

        chat_completion = await self.client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            model=self.model,
            temperature=0.1,  # Low temperature for code
            response_format=response_format,
        )
        content = chat_completion.choices[0].message.content
        LOGGER.info("Groq response received (length=%d)", len(content or ""))
        return content or ""
