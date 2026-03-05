"""
FlowExecution ORM model — maps to the `flow_executions` PostgreSQL table.

ExecutionStatus is a str enum so FastAPI can serialize it directly to/from
JSON strings without additional conversion. Values must match the DB CHECK
constraint exactly (Coding Standard 4 — consistency).
"""
from __future__ import annotations

import enum
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text, func, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ExecutionStatus(str, enum.Enum):
    """Valid flow execution statuses — must match DB CHECK constraint."""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED_HITL = "paused_hitl"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class FlowExecution(Base):
    __tablename__ = "flow_executions"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("uuid_generate_v4()"),
    )
    flow_id: Mapped[Optional[UUID]] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("flows.id"),
        nullable=True,
    )
    # Stored as VARCHAR in DB; ExecutionStatus enum used in the Python layer
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default=ExecutionStatus.PENDING.value
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    total_steps: Mapped[int] = mapped_column(Integer, nullable=False)
    completed_steps: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    current_step: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    # DECIMAL(5,2): e.g. 98.50 — matches DB column precision
    success_rate: Mapped[Optional[object]] = mapped_column(
        Numeric(5, 2), nullable=True
    )
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    execution_metadata: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
