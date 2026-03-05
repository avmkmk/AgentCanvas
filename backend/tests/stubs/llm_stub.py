"""
Stub for LLMService (BC-01) — used by unit tests before implementation.

This stub mirrors the expected public interface of the real LLMService
so tests can be written and run today without a real Anthropic API key.
The stub is intentionally minimal — it covers only the contract surface
needed for unit tests.

Coding Standard 8: third-party dependencies are wrapped in service classes.
The stub validates that interface here.
"""
from __future__ import annotations

import asyncio


class LLMServiceStub:
    """
    Minimal stub matching the expected LLMService interface.

    Parameters
    ----------
    response:
        String to return on a successful complete() call.
    fail_times:
        Number of times complete() raises RuntimeError before succeeding.
        Simulates transient network errors.
    """

    def __init__(self, response: str = "stub response", fail_times: int = 0) -> None:
        self._response = response
        self._fail_times = fail_times
        self._call_count: int = 0

    async def complete(self, prompt: str, *, timeout: float = 30.0) -> str:
        """
        Call LLM with timeout.

        Raises asyncio.TimeoutError if timeout <= 0.
        Raises RuntimeError for the first fail_times calls (transient error).
        """
        if timeout <= 0:
            raise asyncio.TimeoutError("LLM call timed out")
        if self._call_count < self._fail_times:
            self._call_count += 1
            raise RuntimeError("transient LLM error")
        return self._response
