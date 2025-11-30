from __future__ import annotations

import asyncio
import logging
from tenacity import (
    retry,
    stop_after_attempt,
    wait_fixed,
    retry_if_exception_type,
    before_sleep_log,
)

from backend.utils.logging import get_logger

from .adapter import BaseLLMAdapter

LOGGER = get_logger(__name__)


class OllamaLLMAdapter(BaseLLMAdapter):
    """Invoke local Ollama CLI asynchronously."""

    def __init__(self, model: str = "llama3"):
        self.model = model

    @retry(
        retry=retry_if_exception_type(RuntimeError),
        wait=wait_fixed(2),  # Wait 2 seconds between local retries
        stop=stop_after_attempt(3),
        before_sleep=before_sleep_log(LOGGER, logging.WARNING),
    )
    async def acomplete(self, prompt: str, json_mode: bool = False) -> str:
        LOGGER.info("Calling Ollama with model '%s' (json_mode=%s)", self.model, json_mode)
        
        cmd = ["ollama", "run", self.model]
        if json_mode:
            cmd.extend(["--format", "json"])
            
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate(prompt.encode("utf-8"))
            if process.returncode != 0:
                error_msg = stderr.decode("utf-8")
                LOGGER.error("Ollama failed: %s", error_msg)
                raise RuntimeError(
                    f"Ollama exited with {process.returncode}: {error_msg}"
                )
            result = stdout.decode("utf-8")
            
            if not result.strip():
                LOGGER.warning("Ollama returned empty response.")
                # Try one retry if empty
                raise RuntimeError("Empty response from Ollama")

            LOGGER.info("Ollama response received (length=%d)", len(result))
            return result
        except Exception as exc:
             LOGGER.error("Exception calling Ollama: %s", exc)
             raise
