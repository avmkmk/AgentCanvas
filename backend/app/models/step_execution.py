"""
StepExecution ORM model — maps to the `step_executions` PostgreSQL table.

One row per agent step within a flow execution.
input_data and output_data store the full LLM input/output as JSONB
for auditability and replay capability (Coding Standard 10).
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class StepExecution(Base):
    __tablename__ = "step_executions"

    id: Mapped[UUID] = mapped_column(
        sa.Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    execution_id: Mapped[Optional[UUID]] = mapped_column(
        sa.Uuid(as_uuid=True),
        ForeignKey("flow_executions.id", ondelete="CASCADE"),
        nullable=True,
    )
    agent_id: Mapped[Optional[UUID]] = mapped_column(
        sa.Uuid(as_uuid=True),
        ForeignKey("agents.id"),
        nullable=True,
    )
    step_number: Mapped[int] = mapped_column(Integer, nullable=False)
    input_data: Mapped[Optional[dict]] = mapped_column(sa.JSON, nullable=True)
    output_data: Mapped[Optional[dict]] = mapped_column(sa.JSON, nullable=True)
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="pending"
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    execution_time_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
