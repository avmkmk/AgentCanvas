"""
LLM service — wraps the Anthropic client.

Coding Standard 8: all LLM calls go through this service class so the
rest of the application never touches the SDK directly. This makes it
easy to mock in tests and to swap providers later.

M1 status: stub only — full implementation is tracked in backlog item
LLM-01 (M3). The class exists now so conftest.py's mock_llm fixture
can patch it without a ModuleNotFoundError.
"""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

# Maximum time to wait for any single LLM call (Coding Standard 5)
_LLM_TIMEOUT_SECONDS: int = 120

# Maximum allowed length for a validated LLM response (Coding Standard 9)
_MAX_RESPONSE_CHARS: int = 50_000


class LLMService:
    """Thin wrapper around the Anthropic client.

    Validates every response before returning it to callers (Coding
    Standard 8). All errors are re-raised as LLMError so callers do
    not need to know which provider is in use.
    """

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

        This method is intentionally thin in M1. It will be filled in
        during M3 (LLM-01) when the agent execution pipeline is built.

        Args:
            model: Model identifier string (e.g. ``claude-opus-4-6``).
            prompt: User-turn text, already sanitized by the caller.
            system_prompt: Static system prompt from the agent template.
            temperature: Sampling temperature (0.0–1.0).
            max_tokens: Maximum tokens to generate.

        Returns:
            Non-empty text content string from the model.

        Raises:
            NotImplementedError: Always in M1 — full impl is in M3.
        """
        # NOTE: stub raises to catch accidental calls in unit tests that
        # forget to inject mock_llm. Real implementation goes here in M3.
        raise NotImplementedError(
            "LLMService.complete is not implemented in M1. "
            "Use the mock_llm fixture in tests."
        )
