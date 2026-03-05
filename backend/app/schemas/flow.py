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
from datetime import datetime
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
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class FlowListResponse(BaseModel):
    """Paginated list of flows."""

    items: list[FlowResponse]
    total: int
    page: int
    page_size: int
    pages: int


# ─── Agent schemas ────────────────────────────────────────────────────────────

# Literal type surfaces the enum in OpenAPI docs and enables static analysis
AgentRoleLiteral = Literal[
    "researcher", "analyst", "writer", "critic", "planner", "custom"
]

# Only "conversational" is supported in MVP — matches Agent ORM VALID_TYPES
_DEFAULT_AGENT_TYPE: str = "conversational"


class AgentCreate(BaseModel):
    """
    Schema for creating an agent under a flow.

    Reconciled with Agent ORM columns (BA-15):
      name, role, type, system_prompt, model_name, config
    system_prompt is sanitized by AgentService before storage (SECURITY.md).
    """

    name: str = Field(..., min_length=1, max_length=100)
    # Use Literal for OpenAPI enum + static analysis
    role: AgentRoleLiteral = Field(
        ..., description="One of: researcher | analyst | writer | critic | planner | custom"
    )
    # type defaults to "conversational" — the only MVP-supported agent type
    type: str = Field(default=_DEFAULT_AGENT_TYPE, min_length=1, max_length=50)
    # system_prompt: sanitize_prompt() is applied in AgentService, not here,
    # so the raw value is preserved for display while the stored value is safe.
    system_prompt: str = Field(..., min_length=1, max_length=10_000)
    model_name: str = Field(..., min_length=1, max_length=100)
    config: dict[str, Any] = Field(default_factory=dict)

    @field_validator("name")
    @classmethod
    def name_no_dangerous_chars(cls, value: str) -> str:
        return _validate_name(value)


class AgentUpdate(BaseModel):
    """
    Partial update schema for agents — all fields optional.

    Uses exclude_unset=True in AgentService so only supplied fields are written.
    """

    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    role: Optional[AgentRoleLiteral] = None
    type: Optional[str] = Field(default=None, min_length=1, max_length=50)
    system_prompt: Optional[str] = Field(default=None, min_length=1, max_length=10_000)
    model_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    config: Optional[dict[str, Any]] = None

    @field_validator("name")
    @classmethod
    def name_no_dangerous_chars(cls, value: Optional[str]) -> Optional[str]:
        if value is not None:
            return _validate_name(value)
        return value


class AgentResponse(BaseModel):
    """
    Response schema for Agent — mirrors Agent ORM columns exactly (BA-15).

    Fields removed vs old schema: agent_type, step_order, is_active.
    Fields added:                  type, system_prompt, model_name.
    """

    id: UUID
    flow_id: Optional[UUID]
    name: str
    role: str
    type: str
    system_prompt: str
    model_name: str
    config: Optional[dict[str, Any]]
    # datetime — not str — so Pydantic serialises the ORM datetime correctly
    created_at: datetime

    model_config = {"from_attributes": True}
