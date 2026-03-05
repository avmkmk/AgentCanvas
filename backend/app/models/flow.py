"""
Flow ORM model — maps to the `flows` PostgreSQL table.

Flows are the top-level entity: a directed graph of agents stored as
canvas JSON (nodes + edges) in flow_config JSONB column.

Type notes:
- sa.Uuid: cross-dialect UUID type (renders as UUID on PG, CHAR(32) on SQLite)
- sa.JSON: cross-dialect JSON type (renders as JSON on all dialects;
  the production migration uses JSONB explicitly for PG GIN-index support)
"""
from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Optional
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy import Boolean, String, Text, true
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.agent import Agent


class Flow(Base, TimestampMixin):
    __tablename__ = "flows"

    # sa.Uuid: cross-dialect — UUID on PG, CHAR(32) on SQLite.
    # default=uuid.uuid4 generates UUIDs in Python so SQLite tests work without
    # the uuid-ossp PG extension.
    id: Mapped[UUID] = mapped_column(
        sa.Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # Stores canvas serialization: {"nodes": [...], "edges": [...]}
    # sa.JSON is cross-dialect; production migration enforces JSONB on PG.
    flow_config: Mapped[dict] = mapped_column(sa.JSON, nullable=False)
    created_by: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    # Soft-delete flag: inactive flows are hidden from default list queries
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=true(),
    )

    # cascade="all, delete-orphan": deleting a Flow deletes its Agents
    agents: Mapped[list["Agent"]] = relationship(
        "Agent",
        back_populates="flow",
        cascade="all, delete-orphan",
    )
