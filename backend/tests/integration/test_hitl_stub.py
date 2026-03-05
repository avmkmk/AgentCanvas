"""
Stub integration tests for HITL gate end-to-end (T-06).

These tests are marked xfail because they require:
  - HITLManager (BC-06) wired into the API layer
  - FlowExecutor (BC-02) integrated with the HITL pause/resume mechanism
  - A real or test DB with hitl_reviews table populated

When BC-06 and BC-02 are implemented and the HITL API endpoints are
registered in main.py, remove the xfail markers and replace the stubs
with real async_client calls.

Coding Standard 5: every test asserts a specific HTTP status, not a
generic truthy check.
"""
from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.stubs.hitl_stub import HITLManagerStub


# ─────────────────────────────────────────────────────────────────────────────
# Stub-level integration: verify stub state machine in create→approve/reject
# flow (these run now, no xfail)
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_stub_create_review_returns_pending_status() -> None:
    """
    A freshly created HITL review must start in 'pending' status.
    Documents the contract that the HTTP POST /hitl/reviews endpoint
    must also return status='pending'.
    """
    mgr = HITLManagerStub()
    review = await mgr.create_review(execution_id="exec-1")
    assert review.status == "pending", (
        "New HITL review must have status 'pending'"
    )


@pytest.mark.asyncio
async def test_stub_approved_review_allows_execution_to_continue() -> None:
    """
    Approving a pending HITL review transitions it to 'approved'.
    Documents the expected behaviour of the HITL approve endpoint.
    """
    mgr = HITLManagerStub()
    review = await mgr.create_review(execution_id="exec-2")
    review.approve()
    assert review.status == "approved", (
        "Approving a review must transition it to 'approved'"
    )


@pytest.mark.asyncio
async def test_stub_rejected_review_cancels_execution() -> None:
    """
    Rejecting a pending HITL review transitions it to 'rejected'.
    Documents the expected behaviour of the HITL reject endpoint.
    """
    mgr = HITLManagerStub()
    review = await mgr.create_review(execution_id="exec-3")
    review.reject()
    assert review.status == "rejected", (
        "Rejecting a review must transition it to 'rejected'"
    )


# ─────────────────────────────────────────────────────────────────────────────
# API-level integration tests (xfail until BC-06 + HITL router registered)
# ─────────────────────────────────────────────────────────────────────────────

_API_KEY = "test-api-key-for-unit-tests"
_AUTH_HEADERS = {"X-API-Key": _API_KEY}


@pytest.mark.xfail(
    reason="HITLManager (BC-06) + execution engine not implemented",
    strict=False,
)
@pytest.mark.asyncio
async def test_create_hitl_review_returns_pending_status(
    async_client: AsyncClient,
) -> None:
    """
    POST /api/v1/executions/{execution_id}/hitl must return a review
    with status='pending'.

    Requires:
    - Execution engine creating a paused_hitl execution
    - HITL router registered in main.py
    """
    # This call will 404 until the HITL router is registered
    response = await async_client.post(
        "/api/v1/executions/fake-execution-id/hitl",
        headers=_AUTH_HEADERS,
    )
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "pending"


@pytest.mark.xfail(
    reason="HITLManager (BC-06) + execution engine not implemented",
    strict=False,
)
@pytest.mark.asyncio
async def test_approved_review_allows_execution_to_continue(
    async_client: AsyncClient,
) -> None:
    """
    POST /api/v1/hitl/{review_id}/approve must:
    1. Set review status to 'approved'
    2. Trigger the paused execution to resume

    Requires BC-06 + BC-02 integration.
    """
    response = await async_client.post(
        "/api/v1/hitl/fake-review-id/approve",
        json={"decision": "approved", "reviewed_by": "test-operator"},
        headers=_AUTH_HEADERS,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "approved"
    # Real test would also assert execution status changed to "running"


@pytest.mark.xfail(
    reason="HITLManager (BC-06) + execution engine not implemented",
    strict=False,
)
@pytest.mark.asyncio
async def test_rejected_review_cancels_execution(
    async_client: AsyncClient,
) -> None:
    """
    POST /api/v1/hitl/{review_id}/reject must:
    1. Set review status to 'rejected'
    2. Cancel the paused execution

    Requires BC-06 + BC-02 integration.
    """
    response = await async_client.post(
        "/api/v1/hitl/fake-review-id/reject",
        json={"decision": "rejected", "reviewed_by": "test-operator"},
        headers=_AUTH_HEADERS,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "rejected"
    # Real test would also assert execution status changed to "cancelled"
