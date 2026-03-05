"""
HITLReview ORM model — maps to the `hitl_reviews` PostgreSQL table.

GateType and ReviewStatus are str enums matching the DB CHECK constraints.
output_to_review stores whatever the agent produced for the human reviewer.
"""
from __future__ import annotations

import enum
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, Text, func, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class GateType(str, enum.Enum):
    """HITL gate positions — must match DB CHECK constraint."""
    BEFORE = "before"
    AFTER = "after"
    ON_DEMAND = "on_demand"


class ReviewStatus(str, enum.Enum):
    """HITL review outcomes — must match DB CHECK constraint."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class HITLReview(Base):
    __tablename__ = "hitl_reviews"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("uuid_generate_v4()"),
    )
    execution_id: Mapped[Optional[UUID]] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("flow_executions.id"),
        nullable=True,
    )
    step_id: Mapped[Optional[UUID]] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("step_executions.id"),
        nullable=True,
    )
    agent_id: Mapped[Optional[UUID]] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("agents.id"),
        nullable=True,
    )
    gate_type: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default=ReviewStatus.PENDING.value
    )
    output_to_review: Mapped[dict] = mapped_column(JSONB, nullable=False)
    reviewer_comments: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    reviewed_by: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
