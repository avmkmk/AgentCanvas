"""
Agent ORM model — maps to the `agents` PostgreSQL table.

Agents belong to a Flow and represent one LLM-powered step.
role must be one of the valid values (enforced at DB and Python level
for defence-in-depth per Coding Standard 9).
"""
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, Text, func, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.flow import Flow

# Valid role values — must match the DB CHECK constraint exactly (Coding Standard 4)
VALID_ROLES: frozenset[str] = frozenset(
    {"researcher", "analyst", "writer", "critic", "planner", "custom"}
)
# Only 'conversational' supported in MVP
VALID_TYPES: frozenset[str] = frozenset({"conversational"})


class Agent(Base):
    __tablename__ = "agents"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("uuid_generate_v4()"),
    )
    flow_id: Mapped[Optional[UUID]] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("flows.id", ondelete="CASCADE"),
        nullable=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    system_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    role: Mapped[str] = mapped_column(String(100), nullable=False)
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    # config stores model-specific parameters (temperature, max_tokens, etc.)
    config: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    flow: Mapped[Optional["Flow"]] = relationship("Flow", back_populates="agents")
