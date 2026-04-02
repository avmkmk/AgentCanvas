"""
HITLManager — creates, waits for, and records HITL gate decisions (BC-06).

Design decisions:
- _gate_events is a module-level dict (not instance attribute).  FastAPI runs all
  coroutines on one asyncio event loop per process, so the background task
  (FlowExecutor) and the request handler (HITL API) safely share the same dict.
- wait_for_decision defaults to "rejected" on timeout — safe because a timed-out
  gate stops the execution rather than allowing it to continue unreviewed.
- record_decision returns HTTP 409 if the review is not pending — prevents double
  decisions from race conditions.

Coding Standard 1: no recursion — all async waits use asyncio primitives.
Coding Standard 2: DB session passed in; manager does not own a session.
Coding Standard 5: all errors checked; timeout maps to explicit "rejected".
"""
from __future__ import annotations

import asyncio
import datetime
import logging
import uuid
from typing import TYPE_CHECKING
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.hitl_review import HITLReview, ReviewStatus

if TYPE_CHECKING:
    from app.core.ws_manager import ConnectionManager

_log = logging.getLogger(__name__)

# Module-level dict: review_id (str) → asyncio.Event.
# Shared by FlowExecutor (writer) and HITL API (signaller) on the same event loop.
_gate_events: dict[str, asyncio.Event] = {}


class HITLManager:
    """Stateless service class for HITL gate lifecycle operations.

    All methods are static so callers do not need to instantiate this class.
    """

    @staticmethod
    async def create_review(
        db: AsyncSession,
        execution_id: UUID,
        step_id: UUID,
        agent_id: UUID,
        gate_type: str,
        output_to_review: dict,
        ws_manager: "ConnectionManager",
    ) -> HITLReview:
        """Insert a pending HITLReview row, register its gate event, and broadcast.

        Args:
            db: Async DB session (background task owns this session).
            execution_id: ID of the running FlowExecution.
            step_id: ID of the StepExecution being gated.
            agent_id: ID of the Agent that triggered the gate.
            gate_type: GateType enum value ("before" | "after" | "on_demand").
            output_to_review: Dict payload for the reviewer to inspect.
            ws_manager: Singleton connection manager for broadcasting.

        Returns:
            Persisted HITLReview ORM instance (status=pending).
        """
        review = HITLReview(
            id=uuid.uuid4(),
            execution_id=execution_id,
            step_id=step_id,
            agent_id=agent_id,
            gate_type=gate_type,
            status=ReviewStatus.PENDING.value,
            output_to_review=output_to_review,
        )
        db.add(review)
        await db.commit()
        await db.refresh(review)

        # Register gate event before broadcasting — avoids a race where the
        # decision API fires before wait_for_decision registers the event.
        _gate_events[str(review.id)] = asyncio.Event()

        await ws_manager.broadcast(
            str(execution_id),
            "hitl_review_pending",
            {
                "review_id": str(review.id),
                "agent_id": str(agent_id),
                "gate_type": gate_type,
                "output_to_review": output_to_review,
            },
        )

        _log.info(
            "HITLManager.create_review: review_id=%s execution_id=%s gate=%s",
            review.id,
            execution_id,
            gate_type,
        )
        return review

    @staticmethod
    async def wait_for_decision(
        review_id: UUID,
        timeout_seconds: int,
    ) -> str:
        """Block until the gate event is signalled or the timeout expires.

        Returns "approved" or "rejected".  On timeout, returns "rejected" so
        the caller (FlowExecutor) stops execution cleanly rather than hanging.

        Args:
            review_id: UUID of the HITLReview to wait on.
            timeout_seconds: Maximum seconds to wait before auto-rejecting.

        Returns:
            "approved" or "rejected" string matching ReviewStatus enum values.
        """
        review_id_str = str(review_id)
        event = _gate_events.get(review_id_str)
        if event is None:
            # Event not registered — treat as timeout-rejected (defensive)
            _log.warning(
                "HITLManager.wait_for_decision: no event for review_id=%s — auto-reject",
                review_id_str,
            )
            return ReviewStatus.REJECTED.value

        try:
            await asyncio.wait_for(event.wait(), timeout=float(timeout_seconds))
        except asyncio.TimeoutError:
            _log.warning(
                "HITLManager.wait_for_decision: timeout after %ds for review_id=%s",
                timeout_seconds,
                review_id_str,
            )
            _gate_events.pop(review_id_str, None)
            return ReviewStatus.REJECTED.value

        # Event was signalled — decision has been recorded in DB by record_decision.
        # The status field was set before the event was fired, so it is safe to
        # return the stored value.  We do not fetch it here (no db session);
        # the executor only needs the string "approved" or "rejected".
        _gate_events.pop(review_id_str, None)

        # Return value is set by record_decision via the event's _decision attribute
        # attached on Signal.  Fetch the decision stored on the event object.
        decision: str = getattr(event, "_decision", ReviewStatus.REJECTED.value)
        return decision

    @staticmethod
    async def record_decision(
        db: AsyncSession,
        review_id: UUID,
        decision: str,
        reviewer_comments: str | None,
        reviewed_by: str | None,
        ws_manager: "ConnectionManager",
        execution_id: UUID,
    ) -> HITLReview:
        """Persist the reviewer's decision and signal the waiting gate event.

        Args:
            db: Async DB session (request-scoped from the API handler).
            review_id: UUID of the HITLReview to decide.
            decision: "approved" or "rejected".
            reviewer_comments: Optional free-text comment from reviewer.
            reviewed_by: Optional identity string for the reviewer.
            ws_manager: Singleton connection manager for broadcasting.
            execution_id: Execution to broadcast the decision event to.

        Returns:
            Updated HITLReview ORM instance.

        Raises:
            HTTPException 404: Review not found.
            HTTPException 409: Review already decided (not pending).
        """
        result = await db.execute(
            select(HITLReview).where(HITLReview.id == review_id)
        )
        review = result.scalar_one_or_none()
        if review is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="HITL review not found",
            )

        if review.status != ReviewStatus.PENDING.value:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Review already decided: {review.status}",
            )

        review.status = decision
        review.reviewer_comments = reviewer_comments
        review.reviewed_by = reviewed_by
        review.reviewed_at = datetime.datetime.utcnow()
        await db.commit()
        await db.refresh(review)

        # Signal the waiting background task — attach decision before set()
        # so wait_for_decision can read it from the event object.
        event = _gate_events.get(str(review_id))
        if event is not None:
            event._decision = decision  # type: ignore[attr-defined]  # runtime attr
            event.set()

        await ws_manager.broadcast(
            str(execution_id),
            "hitl_review_decided",
            {
                "review_id": str(review_id),
                "decision": decision,
            },
        )

        _log.info(
            "HITLManager.record_decision: review_id=%s decision=%s",
            review_id,
            decision,
        )
        return review


# Module-level singleton (Coding Standard 4 — one way to do each thing)
hitl_manager = HITLManager()
