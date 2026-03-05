"""
Pydantic v2 response schema for flow memory (MongoDB-backed).

shared_memory and agent_memories are free-form JSONB — validated as dicts.
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
    flow_id is stored as a string in MongoDB but exposed as UUID here.
    """

    flow_id: UUID
    shared_memory: dict[str, Any]
    agent_memories: dict[str, Any]
    metadata: Optional[dict[str, Any]] = None
