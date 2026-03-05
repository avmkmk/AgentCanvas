"""
Flow CRUD router — BA-02 / BA-03.

Thin router: validate input (Pydantic) → call FlowService → return response.
No business logic here (ARCHITECTURE.md layer rule).

Security:
- verify_api_key on every route (SECURITY.md)
- Input validation delegated to FlowCreate / FlowUpdate schemas
- No LLM calls in this router — rate limiting not required here
"""
from __future__ import annotations

import uuid
from math import ceil

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db, verify_api_key
from app.schemas.flow import (
    FlowCreate,
    FlowListResponse,
    FlowResponse,
    FlowUpdate,
)
from app.services.flow_service import FlowService

router = APIRouter(prefix="/flows", tags=["flows"])

# Module-level singleton — FlowService is stateless (no instance state)
_service = FlowService()


@router.post(
    "",
    response_model=FlowResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new flow",
)
async def create_flow(
    data: FlowCreate,
    db: AsyncSession = Depends(get_db),
    _auth: None = Depends(verify_api_key),
) -> FlowResponse:
    """Create a flow and return the persisted record."""
    flow = await _service.create_flow(db=db, data=data)
    return FlowResponse.model_validate(flow)


@router.get(
    "",
    response_model=FlowListResponse,
    summary="List all flows (paginated)",
)
async def list_flows(
    page: int = Query(default=1, ge=1, description="1-based page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Rows per page"),
    db: AsyncSession = Depends(get_db),
    _auth: None = Depends(verify_api_key),
) -> FlowListResponse:
    """Return a paginated list of flows, newest first."""
    items, total = await _service.list_flows(db=db, page=page, page_size=page_size)
    pages = ceil(total / page_size) if page_size > 0 else 0
    return FlowListResponse(
        items=[FlowResponse.model_validate(f) for f in items],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.get(
    "/{flow_id}",
    response_model=FlowResponse,
    summary="Get a single flow by ID",
)
async def get_flow(
    flow_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _auth: None = Depends(verify_api_key),
) -> FlowResponse:
    """Return a flow by its UUID primary key."""
    flow = await _service.get_flow(db=db, flow_id=flow_id)
    if flow is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flow not found",
        )
    return FlowResponse.model_validate(flow)


@router.patch(
    "/{flow_id}",
    response_model=FlowResponse,
    summary="Partially update a flow",
)
async def update_flow(
    flow_id: uuid.UUID,
    data: FlowUpdate,
    db: AsyncSession = Depends(get_db),
    _auth: None = Depends(verify_api_key),
) -> FlowResponse:
    """Apply partial updates to a flow.  Only supplied fields are modified."""
    flow = await _service.update_flow(db=db, flow_id=flow_id, data=data)
    if flow is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flow not found",
        )
    return FlowResponse.model_validate(flow)


@router.delete(
    "/{flow_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a flow",
)
async def delete_flow(
    flow_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _auth: None = Depends(verify_api_key),
) -> None:
    """Hard-delete a flow and all its child agents (DB CASCADE)."""
    deleted = await _service.delete_flow(db=db, flow_id=flow_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flow not found",
        )
