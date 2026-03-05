"""
AgentService — all Agent CRUD business logic for BA-15.

Routers must delegate here and perform no DB operations themselves
(Coding Standard 4 — one responsibility per layer; ARCHITECTURE.md layer rules).

Rules enforced:
- Flow existence is verified before any agent operation (404 if missing)
- system_prompt is sanitized via sanitize_prompt() before storage (SECURITY.md)
- list_agents returns oldest-first (created_at ASC) — canvas renders in order
- update_agent applies only fields explicitly provided (exclude_unset=True)
- delete_agent is a hard DELETE — Agent has no is_active column
- DB exceptions propagate to the caller — no silent swallowing (Coding Standard 5)
"""
from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.agent import Agent
from app.models.flow import Flow
from app.schemas.flow import AgentCreate, AgentUpdate
from app.utils.prompt_sanitizer import sanitize_prompt


class AgentService:
    """CRUD operations for Agent entities. Stateless — safe to share as a singleton."""

    async def _get_flow(
        self,
        db: AsyncSession,
        flow_id: uuid.UUID,
    ) -> Optional[Flow]:
        """Return the Flow row or None. Used to validate flow ownership."""
        result = await db.execute(select(Flow).where(Flow.id == flow_id))
        return result.scalar_one_or_none()

    async def create_agent(
        self,
        db: AsyncSession,
        flow_id: uuid.UUID,
        data: AgentCreate,
    ) -> Agent:
        """
        Persist a new Agent under the given flow and return the ORM instance.

        Raises ValueError if the flow does not exist (caller converts to 404).
        system_prompt is sanitized before storage to remove injection patterns.
        """
        flow = await self._get_flow(db=db, flow_id=flow_id)
        if flow is None:
            raise ValueError(f"Flow {flow_id} not found")

        # Sanitize before storage — SECURITY.md §Prompt Injection Prevention
        safe_prompt: str = sanitize_prompt(data.system_prompt)

        agent = Agent(
            flow_id=flow_id,
            name=data.name,
            role=data.role,
            type=data.type,
            system_prompt=safe_prompt,
            model_name=data.model_name,
            config=data.config if data.config else None,
        )
        db.add(agent)
        await db.commit()
        await db.refresh(agent)
        return agent

    async def list_agents(
        self,
        db: AsyncSession,
        flow_id: uuid.UUID,
    ) -> list[Agent]:
        """
        Return all agents for a flow, ordered oldest-first (canvas render order).

        Returns an empty list if the flow has no agents.
        No 404 check here — caller is responsible for verifying flow existence
        before listing agents (avoids an extra DB round-trip in the happy path).
        """
        result = await db.execute(
            select(Agent)
            .where(Agent.flow_id == flow_id)
            .order_by(Agent.created_at.asc())
        )
        return list(result.scalars().all())

    async def get_agent(
        self,
        db: AsyncSession,
        flow_id: uuid.UUID,
        agent_id: uuid.UUID,
    ) -> Optional[Agent]:
        """
        Return a single Agent by primary key with flow ownership check.

        Returns None if either the agent does not exist or it belongs to a
        different flow (prevents cross-flow data leakage).
        """
        result = await db.execute(
            select(Agent).where(
                Agent.id == agent_id,
                Agent.flow_id == flow_id,
            )
        )
        return result.scalar_one_or_none()

    async def update_agent(
        self,
        db: AsyncSession,
        flow_id: uuid.UUID,
        agent_id: uuid.UUID,
        data: AgentUpdate,
    ) -> Optional[Agent]:
        """
        Apply partial updates to an Agent and return the updated instance.

        Uses exclude_unset=True so callers can PATCH a single field without
        overwriting unrelated fields with None (Coding Standard 3 — explicit).

        If system_prompt is in the update payload, it is re-sanitized.
        Returns None if the agent does not exist or belongs to a different flow.
        """
        agent = await self.get_agent(db=db, flow_id=flow_id, agent_id=agent_id)
        if agent is None:
            return None

        updates: dict = data.model_dump(exclude_unset=True)

        # Re-sanitize system_prompt if it is being updated (SECURITY.md)
        if "system_prompt" in updates and updates["system_prompt"] is not None:
            updates["system_prompt"] = sanitize_prompt(updates["system_prompt"])

        for field_name, new_value in updates.items():
            setattr(agent, field_name, new_value)

        await db.commit()
        await db.refresh(agent)
        return agent

    async def delete_agent(
        self,
        db: AsyncSession,
        flow_id: uuid.UUID,
        agent_id: uuid.UUID,
    ) -> bool:
        """
        Hard-delete an Agent from the database.

        Agent has no is_active column — deletion is permanent.
        Returns True if the agent was found and deleted, False otherwise.
        """
        agent = await self.get_agent(db=db, flow_id=flow_id, agent_id=agent_id)
        if agent is None:
            return False

        await db.delete(agent)
        await db.commit()
        return True
