"""
Agent CRUD router — BA-15.

Thin router: validate input (Pydantic) → call AgentService → return response.
No business logic here (ARCHITECTURE.md layer rule).

Security:
- verify_api_key on every route (SECURITY.md)
- Input validation delegated to AgentCreate / AgentUpdate schemas
- system_prompt sanitized in AgentService, not here
"""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db, verify_api_key
from app.schemas.flow import AgentCreate, AgentResponse, AgentUpdate
from app.services.agent_service import AgentService

router = APIRouter(prefix="/flows", tags=["agents"])

# Module-level singleton — AgentService is stateless (no instance state)
_service = AgentService()


@router.post(
    "/{flow_id}/agents",
    response_model=AgentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create an agent under a flow",
)
async def create_agent(
    flow_id: uuid.UUID,
    data: AgentCreate,
    db: AsyncSession = Depends(get_db),
    _auth: None = Depends(verify_api_key),
) -> AgentResponse:
    """Create an agent and return the persisted record."""
    try:
        agent = await _service.create_agent(db=db, flow_id=flow_id, data=data)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flow not found",
        )
    return AgentResponse.model_validate(agent)


@router.get(
    "/{flow_id}/agents",
    response_model=list[AgentResponse],
    summary="List agents for a flow",
)
async def list_agents(
    flow_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _auth: None = Depends(verify_api_key),
) -> list[AgentResponse]:
    """Return all agents for a flow, ordered by creation time."""
    agents = await _service.list_agents(db=db, flow_id=flow_id)
    return [AgentResponse.model_validate(a) for a in agents]


@router.get(
    "/{flow_id}/agents/{agent_id}",
    response_model=AgentResponse,
    summary="Get a single agent by ID",
)
async def get_agent(
    flow_id: uuid.UUID,
    agent_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _auth: None = Depends(verify_api_key),
) -> AgentResponse:
    """Return an agent by its UUID primary key."""
    agent = await _service.get_agent(db=db, flow_id=flow_id, agent_id=agent_id)
    if agent is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )
    return AgentResponse.model_validate(agent)


@router.patch(
    "/{flow_id}/agents/{agent_id}",
    response_model=AgentResponse,
    summary="Partially update an agent",
)
async def update_agent(
    flow_id: uuid.UUID,
    agent_id: uuid.UUID,
    data: AgentUpdate,
    db: AsyncSession = Depends(get_db),
    _auth: None = Depends(verify_api_key),
) -> AgentResponse:
    """Apply partial updates to an agent. Only supplied fields are modified."""
    agent = await _service.update_agent(
        db=db, flow_id=flow_id, agent_id=agent_id, data=data
    )
    if agent is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )
    return AgentResponse.model_validate(agent)


@router.delete(
    "/{flow_id}/agents/{agent_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an agent",
)
async def delete_agent(
    flow_id: uuid.UUID,
    agent_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _auth: None = Depends(verify_api_key),
) -> None:
    """Hard-delete an agent. Agent has no is_active — deletion is permanent."""
    deleted = await _service.delete_agent(
        db=db, flow_id=flow_id, agent_id=agent_id
    )
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )
