"""
LLM service — wraps the Anthropic client.

Coding Standard 8: all LLM calls go through this service class so the
rest of the application never touches the SDK directly. This makes it
easy to mock in tests and to swap providers later.

M3: full implementation replacing the M1 stub (LLM-01).
"""
from __future__ import annotations

import asyncio
import logging

import anthropic

from app.core.config import settings
from app.utils.prompt_sanitizer import sanitize_prompt

logger = logging.getLogger(__name__)

# Maximum time to wait for any single LLM call (Coding Standard 5)
_LLM_TIMEOUT_SECONDS: int = 120

# Maximum allowed length for a validated LLM response (Coding Standard 9)
_MAX_RESPONSE_CHARS: int = 50_000


class LLMTimeoutError(Exception):
    """Raised when all retry attempts for an LLM call time out."""


class LLMResponseError(Exception):
    """Raised when the LLM response is empty or exceeds the maximum length."""


class LLMService:
    """Thin wrapper around the Anthropic client.

    Validates every response before returning it to callers (Coding
    Standard 8). All errors are re-raised as LLMTimeoutError /
    LLMResponseError so callers do not need to know which provider is in use.

    Retry logic: exponential back-off up to settings.max_llm_retries.
    """

    def __init__(self) -> None:
        # Client is created once; reused across all calls (Coding Standard 2)
        self._client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

    async def complete(
        self,
        *,
        model: str,
        prompt: str,
        system_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2_000,
    ) -> str:
        """Call the LLM and return the text content.

        Sanitizes prompt and system_prompt before sending (SECURITY.md).
        Validates the response is non-empty and within length limits.

        Args:
            model: Model identifier string (e.g. ``claude-haiku-4-5-20251001``).
            prompt: User-turn text; sanitized here before sending.
            system_prompt: System prompt from the agent; sanitized here.
            temperature: Sampling temperature (0.0–1.0).
            max_tokens: Maximum tokens to generate.

        Returns:
            Non-empty text content string from the model.

        Raises:
            LLMResponseError: Response is empty or exceeds _MAX_RESPONSE_CHARS.
            LLMTimeoutError: All retry attempts timed out or hit API errors.
        """
        # Sanitize all user-contributed content before LLM submission (SECURITY.md)
        clean_prompt: str = sanitize_prompt(prompt)
        clean_system: str = sanitize_prompt(system_prompt)

        # Initialize last_exc to a sentinel so mypy knows it's always set
        last_exc: Exception = RuntimeError("No attempts made")

        for attempt in range(settings.max_llm_retries + 1):
            try:
                response = await asyncio.wait_for(
                    self._client.messages.create(
                        model=model,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        system=clean_system,
                        messages=[{"role": "user", "content": clean_prompt}],
                    ),
                    timeout=float(_LLM_TIMEOUT_SECONDS),
                )
            except asyncio.TimeoutError as exc:
                logger.warning(
                    "LLM call timed out on attempt %d/%d: model=%s",
                    attempt + 1,
                    settings.max_llm_retries + 1,
                    model,
                )
                last_exc = exc
                # Exponential back-off between retries (Coding Standard 5)
                await asyncio.sleep(float(2**attempt))
                continue
            except anthropic.APIError as exc:
                logger.warning(
                    "Anthropic API error on attempt %d/%d: %s",
                    attempt + 1,
                    settings.max_llm_retries + 1,
                    exc,
                )
                last_exc = exc
                await asyncio.sleep(float(2**attempt))
                continue

            # Validate response structure — never trust raw LLM output (SECURITY.md).
            # response.content is a union of block types; only TextBlock has .text.
            if not response.content:
                raise LLMResponseError("Empty response from LLM")
            first_block = response.content[0]
            if not isinstance(first_block, anthropic.types.TextBlock):
                raise LLMResponseError(
                    f"Unexpected response block type: {type(first_block).__name__}"
                )
            if not first_block.text:
                raise LLMResponseError("Empty text in LLM response")

            text: str = first_block.text

            if len(text) > _MAX_RESPONSE_CHARS:
                raise LLMResponseError(
                    f"LLM response exceeds maximum length of {_MAX_RESPONSE_CHARS} chars"
                )

            logger.debug(
                "LLM call succeeded: model=%s attempt=%d chars=%d",
                model,
                attempt + 1,
                len(text),
            )
            return text

        raise LLMTimeoutError(
            f"LLM failed after {settings.max_llm_retries + 1} attempt(s)"
        ) from last_exc


# Module-level singleton — imported by AgentRunner (Coding Standard 4)
llm_service = LLMService()
