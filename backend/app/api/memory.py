"""
Memory endpoints — BA-09 (read), BA-10 (update).

Thin router: validate input → call MemoryService → return response.
No business logic here (ARCHITECTURE.md layer rule).

Security:
- verify_api_key on every route (SECURITY.md)
- Input validated by FlowMemoryUpdateRequest schema
"""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends

from app.api.dependencies import verify_api_key
from app.schemas.memory import FlowMemoryResponse, FlowMemoryUpdateRequest
from app.services.memory_service import memory_service

router = APIRouter(prefix="/memory", tags=["memory"])


@router.get(
    "/{flow_id}",
    response_model=FlowMemoryResponse,
    summary="Get flow memory",
)
async def get_flow_memory(
    flow_id: uuid.UUID,
    _auth: None = Depends(verify_api_key),
) -> FlowMemoryResponse:
    """Return the current shared and agent memories for a flow."""
    shared = await memory_service.get_shared_memory(flow_id)
    # Agent memories are stored per-agent; for the GET endpoint we return
    # an empty dict — callers who need per-agent data use the agent_id filter.
    # Full aggregation is deferred to M4 when the UI requires it.
    return FlowMemoryResponse(
        flow_id=flow_id,
        shared_memory=shared,
        agent_memories={},
    )


@router.put(
    "/{flow_id}",
    response_model=FlowMemoryResponse,
    summary="Update flow memory",
)
async def update_flow_memory(
    flow_id: uuid.UUID,
    body: FlowMemoryUpdateRequest,
    _auth: None = Depends(verify_api_key),
) -> FlowMemoryResponse:
    """Merge new values into shared memory and/or a specific agent's memory.

    - If body.shared_memory is set, it is merged into the flow's shared memory.
    - If body.agent_id and body.agent_memory are both set, the agent memory
      is updated for that agent within the flow.
    """
    if body.shared_memory:
        await memory_service.update_shared_memory(flow_id, body.shared_memory)

    if body.agent_id and body.agent_memory:
        await memory_service.update_agent_memory(
            flow_id,
            uuid.UUID(body.agent_id),
            body.agent_memory,
        )

    shared = await memory_service.get_shared_memory(flow_id)
    return FlowMemoryResponse(
        flow_id=flow_id,
        shared_memory=shared,
        agent_memories={},
    )
