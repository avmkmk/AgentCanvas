"""
FlowService — all Flow CRUD business logic.

Routers must delegate here and perform no DB operations themselves
(Coding Standard 4 — one responsibility per layer; ARCHITECTURE.md layer rules).

Rules enforced:
- flow_config defaults to {"nodes": [], "edges": []} when not supplied
- list_flows returns newest-first, paginated
- update_flow applies only fields explicitly provided (exclude_unset=True)
- DB exceptions propagate to the caller — no silent swallowing
"""
from __future__ import annotations

import uuid
from typing import Optional

import sqlalchemy as sa
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.flow import Flow
from app.schemas.flow import FlowCreate, FlowUpdate

# Default canvas config: empty graph that React Flow renders without errors
_DEFAULT_FLOW_CONFIG: dict = {"nodes": [], "edges": []}


class FlowService:
    """CRUD operations for Flow entities. Stateless — safe to share as a singleton."""

    async def create_flow(
        self,
        db: AsyncSession,
        data: FlowCreate,
    ) -> Flow:
        """
        Persist a new Flow row and return the ORM instance.

        flow_config defaults to an empty canvas if the caller omits it or
        supplies an empty dict — the React Flow canvas renders an empty graph
        rather than crashing on missing keys.
        """
        # Coding Standard 2: initialise every variable before use
        resolved_config: dict = data.flow_config if data.flow_config else _DEFAULT_FLOW_CONFIG

        flow = Flow(
            name=data.name,
            description=data.description,
            flow_config=resolved_config,
        )
        db.add(flow)
        await db.commit()
        await db.refresh(flow)
        return flow

    async def get_flow(
        self,
        db: AsyncSession,
        flow_id: uuid.UUID,
    ) -> Optional[Flow]:
        """Return a single Flow by primary key, or None if not found."""
        result = await db.execute(
            select(Flow).where(Flow.id == flow_id)
        )
        return result.scalar_one_or_none()

    async def list_flows(
        self,
        db: AsyncSession,
        page: int,
        page_size: int,
    ) -> tuple[list[Flow], int]:
        """
        Return a page of flows (newest-first) and the total count.

        Returns a 2-tuple: (items, total) where items is the page slice and
        total is the un-paginated row count for building pagination metadata.
        """
        offset = (page - 1) * page_size

        # Count query — only active flows; separate from data query for clarity
        count_result = await db.execute(
            select(func.count(Flow.id)).where(Flow.is_active == sa.true())
        )
        total: int = count_result.scalar_one()

        # Data query — active flows only, newest first, offset/limit for page
        data_result = await db.execute(
            select(Flow)
            .where(Flow.is_active == sa.true())
            .order_by(Flow.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        items: list[Flow] = list(data_result.scalars().all())
        return items, total

    async def update_flow(
        self,
        db: AsyncSession,
        flow_id: uuid.UUID,
        data: FlowUpdate,
    ) -> Optional[Flow]:
        """
        Apply partial updates to a Flow and return the updated instance.

        Uses exclude_unset=True so callers can PATCH a single field without
        overwriting unrelated fields with None (Coding Standard 3 — explicit).

        Returns None if the flow does not exist.
        """
        flow = await self.get_flow(db=db, flow_id=flow_id)
        if flow is None:
            return None

        # Only fields explicitly provided in the request body are applied
        updates: dict = data.model_dump(exclude_unset=True)

        # Guard: never allow flow_config to be set to None.
        # flow_config is a NOT NULL column; if the caller sends
        # {"flow_config": null} Pydantic passes it through as None because
        # FlowUpdate.flow_config is Optional.  Stripping it here prevents an
        # IntegrityError from propagating to the caller (Coding Standard 5).
        if updates.get("flow_config") is None:
            updates.pop("flow_config", None)

        for field_name, new_value in updates.items():
            setattr(flow, field_name, new_value)

        await db.commit()
        await db.refresh(flow)
        return flow

    async def delete_flow(
        self,
        db: AsyncSession,
        flow_id: uuid.UUID,
    ) -> bool:
        """
        Soft-delete a Flow by setting is_active=False.

        Returns True if the flow was found and deactivated, False if the
        flow does not exist.  Soft delete is used (not a SQL DELETE) so
        that flows can be audited or recovered if needed.  The is_active
        flag is also used by list_flows to exclude inactive flows from
        default result sets.
        """
        flow = await self.get_flow(db=db, flow_id=flow_id)
        if flow is None:
            return False

        flow.is_active = False
        await db.commit()
        return True
