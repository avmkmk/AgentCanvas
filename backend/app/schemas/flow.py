"""
Pydantic v2 schemas for Flow and Agent endpoints.

Coding Standard 9: validate at API boundary — length limits on all string fields.
name_no_dangerous_chars rejects shell injection / XSS patterns.
flow_config has a 512 KB size cap to prevent memory exhaustion.
Coding Standard 3: explicit Optional — no implicit None.
"""
from __future__ import annotations

import json
import re
from typing import Any, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

# Valid agent roles — must match DB CHECK constraint and TS AgentRole union
_VALID_ROLES = frozenset(
    {"researcher", "analyst", "writer", "critic", "planner", "custom"}
)

# Pattern that must NOT appear in names (shell injection / XSS guard)
_DANGEROUS_CHARS_RE = re.compile(r"[<>&;|`$'\"\\]")

_MAX_FLOW_CONFIG_BYTES = 512_000  # 512 KB


def _validate_name(value: str) -> str:
    """Shared validator: reject dangerous chars and enforce length."""
    if _DANGEROUS_CHARS_RE.search(value):
        raise ValueError(
            "Name contains disallowed characters: < > & ; | ` $ ' \" \\"
        )
    return value


# ─── Flow schemas ─────────────────────────────────────────────────────────────


class FlowCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    # flow_config holds the React Flow graph serialised as JSON
    flow_config: dict[str, Any] = Field(default_factory=dict)

    @field_validator("name")
    @classmethod
    def name_no_dangerous_chars(cls, value: str) -> str:
        return _validate_name(value)

    @field_validator("flow_config")
    @classmethod
    def flow_config_size_limit(cls, value: dict[str, Any]) -> dict[str, Any]:
        """Reject oversized configs to prevent memory exhaustion."""
        if len(json.dumps(value).encode()) > _MAX_FLOW_CONFIG_BYTES:
            raise ValueError(
                f"flow_config exceeds maximum size of {_MAX_FLOW_CONFIG_BYTES} bytes"
            )
        return value


class FlowUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    flow_config: Optional[dict[str, Any]] = None
    is_active: Optional[bool] = None

    @field_validator("name")
    @classmethod
    def name_no_dangerous_chars(cls, value: Optional[str]) -> Optional[str]:
        if value is not None:
            return _validate_name(value)
        return value

    @field_validator("flow_config")
    @classmethod
    def flow_config_size_limit(
        cls, value: Optional[dict[str, Any]]
    ) -> Optional[dict[str, Any]]:
        if value is not None and len(json.dumps(value).encode()) > _MAX_FLOW_CONFIG_BYTES:
            raise ValueError(
                f"flow_config exceeds maximum size of {_MAX_FLOW_CONFIG_BYTES} bytes"
            )
        return value


class FlowResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    flow_config: dict[str, Any]
    is_active: bool
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}


# ─── Agent schemas ────────────────────────────────────────────────────────────

# Literal type surfaces the enum in OpenAPI docs and enables static analysis
AgentRoleLiteral = Literal[
    "researcher", "analyst", "writer", "critic", "planner", "custom"
]


class AgentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    # Use Literal for OpenAPI enum + static analysis; runtime validation is via Literal
    role: AgentRoleLiteral = Field(
        ..., description="One of: researcher | analyst | writer | critic | planner | custom"
    )
    agent_type: str = Field(default="llm", min_length=1, max_length=50)
    config: dict[str, Any] = Field(default_factory=dict)
    step_order: int = Field(..., ge=0)

    @field_validator("name")
    @classmethod
    def name_no_dangerous_chars(cls, value: str) -> str:
        return _validate_name(value)


class AgentResponse(BaseModel):
    id: UUID
    flow_id: UUID
    name: str
    role: str
    agent_type: str
    config: dict[str, Any]
    step_order: int
    is_active: bool
    created_at: str

    model_config = {"from_attributes": True}
