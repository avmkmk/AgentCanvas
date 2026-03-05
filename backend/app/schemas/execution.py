"""
Pydantic v2 schemas for FlowExecution and StepExecution endpoints.

input_data is limited to 100 KB to prevent oversized payloads
(Security — request body size guard at the schema level).
Literal types on status fields enforce valid enum values on read paths.
"""
from __future__ import annotations

import json
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
    id: UUID
    execution_id: Optional[UUID]
    agent_id: Optional[UUID]
    step_number: int
    input_data: Optional[dict[str, Any]]
    output_data: Optional[dict[str, Any]]
    # Literal enforces valid values even if DB is edited directly
    status: str  # kept as str for flexibility; validated at write time by DB CHECK
    started_at: Optional[str]
    completed_at: Optional[str]
    execution_time_ms: Optional[int]
    error_message: Optional[str]
    retry_count: int

    model_config = {"from_attributes": True}


class ExecutionResponse(BaseModel):
    id: UUID
    flow_id: UUID
    status: ExecutionStatusLiteral
    input_data: dict[str, Any]
    output_data: Optional[dict[str, Any]]
    error_message: Optional[str]
    started_at: Optional[str]
    completed_at: Optional[str]
    execution_time_ms: Optional[int]
    success_rate: Optional[float]
    step_count: int
    created_at: str

    model_config = {"from_attributes": True}
