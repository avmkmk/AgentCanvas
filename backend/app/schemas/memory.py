"""
Pydantic v2 response and request schemas for flow memory endpoints (MongoDB-backed).

shared_memory and agent_memories are free-form JSON — validated as dicts.
Coding Standard 9: accept any dict but never trust raw LLM content in memory;
the MemoryService is responsible for sanitizing before storage.
"""
from __future__ import annotations

from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel


class FlowMemoryResponse(BaseModel):
    """
    Mirrors the MongoDB flow_memory document structure.
    flow_id is stored as a string in MongoDB but exposed as UUID here;
    Pydantic v2 coerces str → UUID automatically.
    """

    flow_id: UUID
    shared_memory: dict[str, Any]
    agent_memories: dict[str, Any]
    metadata: Optional[dict[str, Any]] = None


class FlowMemoryUpdateRequest(BaseModel):
    """Request body for PUT /memory/{flow_id}.

    Either shared_memory or agent_id + agent_memory (or both) may be supplied.
    The endpoint applies whichever parts are present.
    """

    shared_memory: Optional[dict[str, Any]] = None
    # agent_id is passed as a string so the caller does not need to encode a UUID
    agent_id: Optional[str] = None
    agent_memory: Optional[dict[str, Any]] = None
