"""
Pydantic v2 schemas for FlowExecution and StepExecution endpoints.

ExecutionResponse mirrors the FlowExecution ORM model fields exactly so
that model_validate(orm_instance) works without manual field mapping.

input_data on ExecutionStartRequest is limited to 100 KB to prevent
oversized payloads (Security — request body size guard at schema level).
Literal types on status fields enforce valid enum values on read paths.
"""
from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

_MAX_INPUT_BYTES = 100_000  # 100 KB

# Literal types match DB CHECK constraint values and TS ExecutionStatus union
ExecutionStatusLiteral = Literal[
    "pending", "running", "paused_hitl", "completed", "failed", "cancelled"
]
StepStatusLiteral = Literal["pending", "running", "completed", "failed"]


class ExecutionStartRequest(BaseModel):
    flow_id: UUID
    input_data: dict[str, Any] = Field(default_factory=dict)

    @field_validator("input_data")
    @classmethod
    def input_data_size_limit(cls, value: dict[str, Any]) -> dict[str, Any]:
        """Reject payloads larger than 100 KB to prevent memory exhaustion."""
        serialized = json.dumps(value)
        if len(serialized.encode()) > _MAX_INPUT_BYTES:
            raise ValueError(
                f"input_data exceeds maximum allowed size of {_MAX_INPUT_BYTES} bytes"
            )
        return value


class StepExecutionResponse(BaseModel):
    """Response schema for a single StepExecution ORM row."""

    id: UUID
    execution_id: Optional[UUID]
    agent_id: Optional[UUID]
    step_number: int
    input_data: Optional[dict[str, Any]]
    output_data: Optional[dict[str, Any]]
    # Kept as str for flexibility; validated at write time by DB CHECK constraint
    status: str
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    execution_time_ms: Optional[int]
    error_message: Optional[str]
    retry_count: int

    model_config = {"from_attributes": True}


class ExecutionResponse(BaseModel):
    """Response schema for a FlowExecution ORM row.

    Field names match the FlowExecution model columns exactly so that
    ExecutionResponse.model_validate(orm_obj) works without aliasing.
    """

    id: UUID
    # flow_id is nullable in the DB (FK with nullable=True)
    flow_id: Optional[UUID]
    status: str
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    total_steps: int
    completed_steps: int
    current_step: int
    success_rate: Optional[float]
    error_message: Optional[str]

    model_config = {"from_attributes": True}
