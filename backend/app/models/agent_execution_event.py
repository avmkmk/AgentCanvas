"""
AgentExecutionEvent ORM model — maps to `agent_execution_events` table.

One row per agent per execution step. Inserting here fires the
sync_agent_analytics DB trigger which upserts the analytics aggregate.

UNIQUE index on (agent_id, execution_id, step_number) prevents double-
counting if a step is retried and an event is accidentally inserted twice.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Integer, String, func, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AgentExecutionEvent(Base):
    __tablename__ = "agent_execution_events"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("uuid_generate_v4()"),
    )
    agent_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("agents.id", ondelete="CASCADE"),
        nullable=False,
    )
    execution_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("flow_executions.id", ondelete="CASCADE"),
        nullable=False,
    )
    step_number: Mapped[int] = mapped_column(Integer, nullable=False)
    # Only 'completed' or 'failed' — the trigger uses these for analytics tallies
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    execution_time_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    llm_calls: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    hitl_reviews: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )


# NOTE: The UNIQUE index (agent_id, execution_id, step_number) is defined in
# the SQL migration (001_initial.sql). SQLAlchemy does not need to redefine it.
