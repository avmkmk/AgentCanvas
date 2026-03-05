"""
Stub tests for LLMService (BC-01).

Two layers of tests here:

1. Tests marked PASS (no xfail): verify the stub itself behaves correctly.
   These run now and must always pass — they protect the stub's own logic.

2. Tests marked xfail: document the *real* LLMService contract that the
   production implementation (BC-01) must satisfy.  They are written against
   the stub interface and will be repurposed as real tests when BC-01 lands.

Coding Standard 7: both success and failure paths are tested.
"""
from __future__ import annotations

import asyncio

import pytest

from tests.stubs.llm_stub import LLMServiceStub


# ─── Stub self-tests (always run) ─────────────────────────────────────────────


@pytest.mark.asyncio
async def test_stub_returns_configured_response() -> None:
    """The stub must return exactly the response string it was initialised with."""
    stub = LLMServiceStub(response="expected output")
    result = await stub.complete(prompt="do something", timeout=30.0)
    assert result == "expected output"


@pytest.mark.asyncio
async def test_stub_timeout_raises_timeout_error() -> None:
    """
    timeout <= 0 must raise asyncio.TimeoutError.

    This documents the interface contract: callers that pass a non-positive
    timeout should expect a TimeoutError, not a hang.
    """
    stub = LLMServiceStub()
    with pytest.raises(asyncio.TimeoutError):
        await stub.complete(prompt="any prompt", timeout=0)


@pytest.mark.asyncio
async def test_stub_negative_timeout_raises_timeout_error() -> None:
    """Negative timeout values must also raise asyncio.TimeoutError."""
    stub = LLMServiceStub()
    with pytest.raises(asyncio.TimeoutError):
        await stub.complete(prompt="any prompt", timeout=-1.0)


@pytest.mark.asyncio
async def test_stub_transient_error_on_first_call() -> None:
    """
    When fail_times=1, the first call raises RuntimeError.
    The second call succeeds.

    This models a transient network error followed by a successful retry —
    used to test the real LLMService retry logic once BC-01 is implemented.
    """
    stub = LLMServiceStub(response="success after retry", fail_times=1)

    with pytest.raises(RuntimeError, match="transient LLM error"):
        await stub.complete(prompt="try 1", timeout=30.0)

    # Second call must succeed
    result = await stub.complete(prompt="try 2", timeout=30.0)
    assert result == "success after retry"


@pytest.mark.asyncio
async def test_stub_multiple_transient_errors() -> None:
    """
    fail_times=3 means the first 3 calls fail; the 4th succeeds.
    Verifies the fail counter increments correctly.
    """
    stub = LLMServiceStub(response="final success", fail_times=3)

    for attempt in range(3):
        with pytest.raises(RuntimeError):
            await stub.complete(prompt=f"attempt {attempt}", timeout=30.0)

    result = await stub.complete(prompt="attempt 3", timeout=30.0)
    assert result == "final success"


# ─── Production LLMService contract tests (xfail until BC-01) ─────────────────
# These tests document requirements that the REAL LLMService must enforce.
# They are written against the stub interface for now; once BC-01 lands,
# the import below is changed to `from app.services.llm_service import LLMService`
# and xfail is removed.


@pytest.mark.xfail(
    reason="LLMService (BC-01) not implemented — documents empty response rejection requirement",
    strict=False,
)
@pytest.mark.asyncio
async def test_empty_response_should_be_rejected() -> None:
    """
    The real LLMService must raise ValueError when the LLM returns an empty
    string.  An empty response is never valid for a multi-agent workflow step.

    The stub returns the empty string — this test is expected to fail against
    the stub, and will be fixed when BC-01 validates non-empty content.
    """
    stub = LLMServiceStub(response="")
    result = await stub.complete(prompt="generate something", timeout=30.0)
    # Production service must raise; stub will not → test marked xfail
    assert len(result) > 0, "LLMService must reject empty string responses"


@pytest.mark.xfail(
    reason="LLMService (BC-01) not implemented — documents 50k character response size limit",
    strict=False,
)
@pytest.mark.asyncio
async def test_response_over_50k_chars_should_be_rejected() -> None:
    """
    The real LLMService must reject responses > 50,000 characters.

    This matches the security requirement in SECURITY.md:
    'validate response (non-empty, ≤50k chars)'.

    The stub returns whatever it was given — this test documents the future
    production validation and will activate once BC-01 enforces the limit.
    """
    oversized_response = "x" * 50_001
    stub = LLMServiceStub(response=oversized_response)
    result = await stub.complete(prompt="write a lot", timeout=30.0)
    # Production service must raise or truncate; stub passes through → xfail
    assert len(result) <= 50_000, (
        "LLMService must reject responses longer than 50,000 characters"
    )
