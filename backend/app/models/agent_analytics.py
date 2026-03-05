"""
AgentAnalytics ORM model — maps to the `agent_analytics` PostgreSQL table.

One row per agent (UNIQUE on agent_id). This table is an aggregate —
updated exclusively by the sync_agent_analytics DB trigger after each
INSERT into agent_execution_events. Application code must NOT write
to this table directly.
"""
from __future__ import annotations

from typing import Optional
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class AgentAnalytics(Base, TimestampMixin):
    __tablename__ = "agent_analytics"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("uuid_generate_v4()"),
    )
    # UNIQUE enforced at DB level — one aggregate row per agent
    agent_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("agents.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    total_runs: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    successful_runs: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    failed_runs: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    # DECIMAL(10,2) for sub-millisecond precision in averages
    avg_execution_time_ms: Mapped[object] = mapped_column(
        Numeric(10, 2), default=0, nullable=False
    )
    min_execution_time_ms: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )
    max_execution_time_ms: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )
    total_llm_calls: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_hitl_reviews: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_run_at: Mapped[Optional[object]] = mapped_column(DateTime, nullable=True)
