"""
HITL review endpoints — BA-07 (list pending) and BA-08 (record decision).

Thin router: validate input → delegate to HITLManager → return response.
No business logic here (ARCHITECTURE.md layer rule).

Security:
- verify_api_key on every route (SECURITY.md)
- Input validation delegated to HITLDecisionRequest schema (XSS guard included)
- HITLManager.record_decision handles 404 / 409 conflict responses
"""

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db, verify_api_key
from app.core.hitl_manager import HITLManager
from app.core.ws_manager import ws_manager
from app.models.hitl_review import HITLReview, ReviewStatus
from app.schemas.hitl import HITLDecisionRequest, HITLReviewResponse

router = APIRouter(prefix="/hitl", tags=["hitl"])


def _to_response(review: HITLReview) -> HITLReviewResponse:
    """Convert a HITLReview ORM object to its Pydantic response schema.

    Dates are serialised to ISO-8601 strings; None values propagate.
    """
    return HITLReviewResponse(
        id=review.id,
        execution_id=review.execution_id,
        step_id=review.step_id,
        agent_id=review.agent_id,
        gate_type=review.gate_type,  # type: ignore[arg-type]
        status=review.status,  # type: ignore[arg-type]
        output_to_review=review.output_to_review,
        reviewer_comments=review.reviewer_comments,
        created_at=review.created_at.isoformat() if review.created_at else "",
        reviewed_at=review.reviewed_at.isoformat() if review.reviewed_at else None,
        reviewed_by=review.reviewed_by,
    )


@router.get(
    "/pending",
    response_model=list[HITLReviewResponse],
    summary="List pending HITL reviews",
)
async def list_pending_reviews(
    execution_id: Optional[uuid.UUID] = None,
    db: AsyncSession = Depends(get_db),
    _auth: None = Depends(verify_api_key),
) -> list[HITLReviewResponse]:
    """Return all HITL reviews with status=pending.

    Optional query param ``execution_id`` filters results to a single execution.
    Returns an empty list when no pending reviews exist.
    """
    query = select(HITLReview).where(HITLReview.status == ReviewStatus.PENDING.value)
    if execution_id is not None:
        query = query.where(HITLReview.execution_id == execution_id)

    result = await db.execute(query)
    reviews = result.scalars().all()
    return [_to_response(r) for r in reviews]


@router.get(
    "/{review_id}",
    response_model=HITLReviewResponse,
    summary="Get a single HITL review",
)
async def get_review(
    review_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _auth: None = Depends(verify_api_key),
) -> HITLReviewResponse:
    """Return a single HITL review by its ID.

    Returns 404 if the review does not exist.
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
    return _to_response(review)


@router.post(
    "/{review_id}/decision",
    response_model=HITLReviewResponse,
    summary="Submit an approve or reject decision",
)
async def submit_decision(
    review_id: uuid.UUID,
    body: HITLDecisionRequest,
    db: AsyncSession = Depends(get_db),
    _auth: None = Depends(verify_api_key),
) -> HITLReviewResponse:
    """Record a reviewer decision (approved / rejected) for a pending HITL gate.

    Returns 404 if the review does not exist.
    Returns 409 if the review has already been decided.
    Signals the waiting FlowExecutor gate to resume or abort execution.
    """
    # Fetch execution_id before delegating — needed for WS broadcast
    result = await db.execute(
        select(HITLReview).where(HITLReview.id == review_id)
    )
    existing = result.scalar_one_or_none()
    if existing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="HITL review not found",
        )

    # execution_id may be None for on_demand reviews created outside a flow
    execution_id = existing.execution_id or uuid.UUID(int=0)

    review = await HITLManager.record_decision(
        db=db,
        review_id=review_id,
        decision=body.decision,
        reviewer_comments=body.reviewer_comments,
        reviewed_by=body.reviewed_by,
        ws_manager=ws_manager,
        execution_id=execution_id,
    )
    return _to_response(review)
