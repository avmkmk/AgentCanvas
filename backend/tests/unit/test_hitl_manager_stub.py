"""
Stub tests for HITLManager (BC-06).

Two layers of tests:

1. Tests marked PASS: verify the stub's state machine transitions —
   always run.
2. Tests marked xfail: document the real HITLManager contract for BC-06.

The HITL state machine has exactly three states:
  pending → approved  (via approve())
  pending → rejected  (via reject())
  approved / rejected → (terminal — no further transitions)

Coding Standard 3: explicit state strings, no boolean flags.
Coding Standard 5: invalid transitions raise ValueError with a clear message.
Coding Standard 7: every valid and invalid transition is tested.
"""
from __future__ import annotations

import pytest

from tests.stubs.hitl_stub import HITLManagerStub, HITLReview


# ─── Stub self-tests (always run) ─────────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_review_returns_pending_status() -> None:
    """New reviews must always start in 'pending' status."""
    mgr = HITLManagerStub()
    review = await mgr.create_review(execution_id="exec-1")
    assert review.status == "pending"


@pytest.mark.asyncio
async def test_create_review_id_includes_execution_id() -> None:
    """Review id must incorporate the execution_id for traceability."""
    mgr = HITLManagerStub()
    review = await mgr.create_review(execution_id="exec-abc")
    assert "exec-abc" in review.id, (
        "Review id must reference the execution_id for correlation in logs"
    )


def test_approve_transitions_status_to_approved() -> None:
    """approve() on a pending review must set status to 'approved'."""
    review = HITLReview(id="review-1")
    review.approve()
    assert review.status == "approved"


def test_reject_transitions_status_to_rejected() -> None:
    """reject() on a pending review must set status to 'rejected'."""
    review = HITLReview(id="review-2")
    review.reject()
    assert review.status == "rejected"


def test_cannot_approve_already_approved_review() -> None:
    """
    Calling approve() on an already-approved review must raise ValueError.
    This prevents double-action bugs in the UI (operator clicks Approve
    twice after a race condition).
    """
    review = HITLReview(id="review-3")
    review.approve()

    with pytest.raises(ValueError, match="approved"):
        review.approve()


def test_cannot_reject_already_rejected_review() -> None:
    """
    Calling reject() on an already-rejected review must raise ValueError.
    """
    review = HITLReview(id="review-4")
    review.reject()

    with pytest.raises(ValueError, match="rejected"):
        review.reject()


def test_cannot_approve_already_rejected_review() -> None:
    """
    Calling approve() on a rejected review must raise ValueError.
    Once rejected, a review cannot be retroactively approved.
    """
    review = HITLReview(id="review-5")
    review.reject()

    with pytest.raises(ValueError, match="rejected"):
        review.approve()


def test_cannot_reject_already_approved_review() -> None:
    """
    Calling reject() on an approved review must raise ValueError.
    Once approved, a review cannot be retroactively rejected.
    """
    review = HITLReview(id="review-6")
    review.approve()

    with pytest.raises(ValueError, match="approved"):
        review.reject()


def test_initial_status_is_pending() -> None:
    """Reviews created directly must start in 'pending' state."""
    review = HITLReview(id="review-7")
    assert review.status == "pending"


# ─── Production HITLManager contract tests (xfail until BC-06) ────────────────


@pytest.mark.xfail(
    reason="HITLManager (BC-06) not implemented — DB persistence required",
    strict=False,
)
@pytest.mark.asyncio
async def test_review_persists_to_database() -> None:
    """
    The real HITLManager must write the review to the hitl_reviews table
    so that a second service instance can retrieve it by id.

    The stub uses an in-process dataclass — a second HITLManagerStub
    instance created after the write will not see the review.
    This test asserts the cross-instance visibility requirement and will
    genuinely fail against the stub (as expected by xfail).
    """
    mgr_writer = HITLManagerStub()
    review = await mgr_writer.create_review(execution_id="exec-persist")

    # Simulate querying by the stored review's id through a separate manager instance.
    # The real HITLManager would expose a get_review(id) method backed by the DB.
    # The stub has no such method — asserting its existence is what causes xfail.
    mgr_reader = HITLManagerStub()
    assert hasattr(mgr_reader, "get_review"), (
        "Real HITLManager must expose get_review(id) to look up persisted reviews"
    )
    found = await mgr_reader.get_review(review.id)  # type: ignore[attr-defined]
    assert found is not None, (
        "Real HITLManager must persist reviews to DB so other instances can read them"
    )


@pytest.mark.xfail(
    reason="HITLManager (BC-06) not implemented — execution resume signalling required",
    strict=False,
)
@pytest.mark.asyncio
async def test_approved_review_allows_execution_to_continue() -> None:
    """
    After approve(), the real HITLManager must signal the paused execution
    to resume.  The test checks that a fake execution_status attribute is
    updated — something the stub never does.

    The stub has no execution_status tracking, so this will xfail correctly.
    """
    mgr = HITLManagerStub()
    review = await mgr.create_review(execution_id="exec-continue")
    review.approve()

    # Real HITLManager would update the flow_execution row status to "running"
    # The stub has no such mechanism, so execution_status attribute is absent
    assert hasattr(review, "execution_status"), (
        "Real HITLManager must expose execution_status on the review after approval"
    )
    assert review.execution_status == "running"  # type: ignore[attr-defined]


@pytest.mark.xfail(
    reason="HITLManager (BC-06) not implemented — execution cancellation required",
    strict=False,
)
@pytest.mark.asyncio
async def test_rejected_review_cancels_execution() -> None:
    """
    After reject(), the real HITLManager must mark the flow execution as
    'cancelled'.  The stub has no execution_status tracking, so this will
    xfail correctly.
    """
    mgr = HITLManagerStub()
    review = await mgr.create_review(execution_id="exec-cancel")
    review.reject()

    # Real HITLManager would update the flow_execution row status to "cancelled"
    assert hasattr(review, "execution_status"), (
        "Real HITLManager must expose execution_status on the review after rejection"
    )
    assert review.execution_status == "cancelled"  # type: ignore[attr-defined]
