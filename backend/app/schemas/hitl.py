"""
Pydantic v2 schemas for HITL review endpoints.

reviewer_comments has a 2000-char limit and injection/XSS check.
reviewed_by has a 255-char limit and name-safety check.
decision must be one of "approved" or "rejected" — matches ReviewStatus enum.
Literal types on gate_type and status enforce valid enum values on read paths.
"""
from __future__ import annotations

import re
from typing import Any, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

# Matches the dangerous-chars pattern in flow.py — keep in sync
_DANGEROUS_CHARS_RE = re.compile(r"[<>&;|`$'\"\\]")

_VALID_DECISIONS = frozenset({"approved", "rejected"})

# Literal types match DB CHECK constraint values
GateTypeLiteral = Literal["before", "after", "on_demand"]
ReviewStatusLiteral = Literal["pending", "approved", "rejected"]


class HITLDecisionRequest(BaseModel):
    decision: str = Field(..., description="One of: approved | rejected")
    reviewer_comments: Optional[str] = Field(default=None, max_length=2000)
    reviewed_by: Optional[str] = Field(default=None, max_length=255)

    @field_validator("decision")
    @classmethod
    def decision_must_be_valid(cls, value: str) -> str:
        if value not in _VALID_DECISIONS:
            raise ValueError("decision must be 'approved' or 'rejected'")
        return value

    @field_validator("reviewed_by")
    @classmethod
    def reviewed_by_no_dangerous_chars(cls, value: Optional[str]) -> Optional[str]:
        """Prevent XSS / injection in identity field stored and displayed in UI."""
        if value is not None and _DANGEROUS_CHARS_RE.search(value):
            raise ValueError(
                "reviewed_by contains disallowed characters: < > & ; | ` $ ' \" \\"
            )
        return value

    @field_validator("reviewer_comments")
    @classmethod
    def reviewer_comments_no_dangerous_chars(
        cls, value: Optional[str]
    ) -> Optional[str]:
        """
        Sanitize free-text comments against script-tag and prompt-injection patterns.
        Rejects angle brackets and backticks — the primary XSS/injection vectors.
        Free-text allows most punctuation; only the highest-risk chars are blocked.
        """
        if value is not None and _DANGEROUS_CHARS_RE.search(value):
            raise ValueError(
                "reviewer_comments contains disallowed characters: < > & ; | ` $ ' \" \\"
            )
        return value


class HITLReviewResponse(BaseModel):
    id: UUID
    execution_id: Optional[UUID]
    step_id: Optional[UUID]
    agent_id: Optional[UUID]
    gate_type: GateTypeLiteral
    status: ReviewStatusLiteral
    output_to_review: dict[str, Any]
    reviewer_comments: Optional[str]
    created_at: str
    reviewed_at: Optional[str]
    reviewed_by: Optional[str]

    model_config = {"from_attributes": True}
