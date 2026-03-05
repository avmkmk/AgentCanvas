"""
Flow ORM model — maps to the `flows` PostgreSQL table.

Flows are the top-level entity: a directed graph of agents stored as
canvas JSON (nodes + edges) in flow_config JSONB column.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import String, Text, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.agent import Agent


class Flow(Base, TimestampMixin):
    __tablename__ = "flows"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("uuid_generate_v4()"),
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # Stores canvas serialization: {"nodes": [...], "edges": [...]}
    flow_config: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_by: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # cascade="all, delete-orphan": deleting a Flow deletes its Agents
    agents: Mapped[list["Agent"]] = relationship(
        "Agent",
        back_populates="flow",
        cascade="all, delete-orphan",
    )
