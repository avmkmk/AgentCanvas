"""
LLM service — wraps the Azure OpenAI client pointed at the EPAM AI Dial proxy.

Coding Standard 8: all LLM calls go through this service class so the
rest of the application never touches the SDK directly. This makes it
easy to mock in tests and to swap providers later.

The EPAM AI Dial proxy (https://ai-proxy.lab.epam.com) is Azure
OpenAI-compatible — one API key routes to all available models (gpt-4o,
gemini-flash, etc.). No per-model credentials are needed.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Optional

import openai
from openai import AsyncAzureOpenAI

from app.core.config import settings
from app.utils.prompt_sanitizer import sanitize_prompt

logger = logging.getLogger(__name__)

# Hard upper bound per LLM call — separate from the configurable timeout so
# we always have a safety net even if config is misconfigured (Coding Standard 5)
_HARD_TIMEOUT_SECONDS: int = 120

# Maximum allowed length for a validated LLM response (Coding Standard 9)
_MAX_RESPONSE_CHARS: int = 50_000


class LLMTimeoutError(Exception):
    """Raised when all retry attempts for an LLM call time out."""


class LLMResponseError(Exception):
    """Raised when the LLM response is empty or exceeds the maximum length."""


class LLMService:
    """Thin wrapper around the Azure OpenAI client targeting EPAM AI Dial.

    Validates every response before returning it to callers (Coding
    Standard 8). All errors are re-raised as LLMTimeoutError /
    LLMResponseError so callers do not need to know which provider is in use.

    Retry logic: exponential back-off up to settings.max_llm_retries.
    Model list is fetched once from the proxy and cached in memory.
    """

    def __init__(self) -> None:
        # Client is created once; reused across all calls (Coding Standard 2).
        # azure_endpoint — base URL of the Dial proxy (e.g. https://ai-proxy.lab.epam.com)
        # api_key        — single Dial API key; routes to all models
        # api_version    — Azure OpenAI API version (e.g. 2024-02-01)
        self._client: AsyncAzureOpenAI = AsyncAzureOpenAI(
            azure_endpoint=settings.dial_endpoint,
            api_key=settings.dial_api_key,
            api_version=settings.dial_api_version,
        )
        # Cache for available model IDs — populated on first call to list_models()
        self._cached_models: Optional[list[str]] = None

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
            model: Deployment name on the Dial proxy (e.g. ``gpt-4o``).
            prompt: User-turn text; sanitized before sending.
            system_prompt: System prompt from the agent; sanitized before sending.
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

        # Initialize last_exc so mypy knows it's always set before use
        last_exc: Exception = RuntimeError("No attempts made")

        for attempt in range(settings.max_llm_retries + 1):
            try:
                response = await asyncio.wait_for(
                    self._client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": clean_system},
                            {"role": "user", "content": clean_prompt},
                        ],
                        temperature=temperature,
                        max_tokens=max_tokens,
                    ),
                    timeout=float(_HARD_TIMEOUT_SECONDS),
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
            except openai.APIError as exc:
                logger.warning(
                    "OpenAI/Dial API error on attempt %d/%d: %s",
                    attempt + 1,
                    settings.max_llm_retries + 1,
                    exc,
                )
                last_exc = exc
                await asyncio.sleep(float(2**attempt))
                continue

            # Validate response — never trust raw LLM output (SECURITY.md / Coding Standard 8)
            if not response.choices:
                raise LLMResponseError("Empty choices list in LLM response")

            message = response.choices[0].message
            if message is None or not message.content:
                raise LLMResponseError("Empty content in LLM response")

            text: str = message.content

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

    async def list_models(self) -> list[str]:
        """Return the list of model deployment names available on the Dial proxy.

        Queries the proxy's /models endpoint once and caches the result
        in memory for the lifetime of this process. If the request fails,
        returns a safe fallback list containing only the configured default
        model so the application can still start up (Coding Standard 5).

        Returns:
            Sorted list of model ID strings (e.g. ["gpt-4o", "gpt-4o-mini"]).
        """
        # Return cached result — avoids a network call on every /api/models request
        if self._cached_models is not None:
            return self._cached_models

        try:
            response = await asyncio.wait_for(
                self._client.models.list(),
                timeout=10.0,  # Short timeout — discovery only; must not block startup
            )
            model_ids: list[str] = sorted(
                model.id for model in response.data if model.id
            )
            if not model_ids:
                # Proxy returned an empty list — fall back to configured default
                logger.warning(
                    "Dial proxy returned empty model list; falling back to default"
                )
                model_ids = [settings.llm_model]
            self._cached_models = model_ids
            logger.info("Dial proxy models cached: %s", model_ids)
            return self._cached_models
        except Exception as exc:
            # Non-fatal — return fallback so the rest of the app still works
            logger.warning(
                "Failed to fetch model list from Dial proxy (%s); "
                "using configured default '%s'",
                exc,
                settings.llm_model,
            )
            # Do NOT cache the fallback — retry on next request in case proxy was
            # temporarily unavailable at startup
            return [settings.llm_model]


# Module-level singleton — imported by AgentRunner and the models router
# (Coding Standard 4: one instance, consistent state)
llm_service = LLMService()
