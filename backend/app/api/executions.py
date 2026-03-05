"""
Execution endpoints — BA-04 (start), BA-05 (status), BA-06 (cancel).

Thin router: validate input → delegate to FlowExecutor → return response.
No business logic here (ARCHITECTURE.md layer rule).

Security:
- verify_api_key on every route (SECURITY.md)
- Input validation delegated to ExecutionStartRequest schema
- Rate limiting on POST (LLM-calling endpoint) — 10/minute per IP
"""
from __future__ import annotations

import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db, verify_api_key
from app.core.executor import flow_executor
from app.models.flow_execution import FlowExecution
from app.schemas.execution import ExecutionResponse, ExecutionStartRequest

router = APIRouter(prefix="/executions", tags=["executions"])

# Rate limiter — keyed by remote IP (SECURITY.md — rate limiting on LLM endpoints)
limiter = Limiter(key_func=get_remote_address)


@router.post(
    "",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=ExecutionResponse,
    summary="Start a flow execution",
)
@limiter.limit("10/minute")
async def start_execution(
    request: Request,
    body: ExecutionStartRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    _auth: None = Depends(verify_api_key),
) -> ExecutionResponse:
    """Start executing a flow in the background and return the execution record.

    Returns 202 Accepted — the execution runs asynchronously.
    Returns 404 if the flow_id does not exist.
    """
    execution = await flow_executor.start(
        db=db,
        flow_id=body.flow_id,
        background_tasks=background_tasks,
    )
    return ExecutionResponse.model_validate(execution)


@router.get(
    "/{execution_id}",
    response_model=ExecutionResponse,
    summary="Get execution status",
)
async def get_execution(
    execution_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _auth: None = Depends(verify_api_key),
) -> ExecutionResponse:
    """Return the current status of a flow execution by its ID."""
    result = await db.execute(
        select(FlowExecution).where(FlowExecution.id == execution_id)
    )
    execution = result.scalar_one_or_none()
    if execution is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Execution not found",
        )
    return ExecutionResponse.model_validate(execution)


@router.post(
    "/{execution_id}/cancel",
    response_model=ExecutionResponse,
    summary="Cancel a running execution",
)
async def cancel_execution(
    execution_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _auth: None = Depends(verify_api_key),
) -> ExecutionResponse:
    """Cancel a running or paused execution.

    Returns 404 if the execution does not exist.
    No-op if the execution is already in a terminal state.
    """
    execution = await flow_executor.cancel(db=db, execution_id=execution_id)
    if execution is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Execution not found",
        )
    return ExecutionResponse.model_validate(execution)


# TODO(BC-07): Add GET /executions/{execution_id}/steps endpoint once
# StepExecution read path is needed by the frontend. Model exists at
# app/models/step_execution.py and schema at StepExecutionResponse.
