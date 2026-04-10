"""
AnalyticsService — read-only queries over agent_analytics (BA-11 / BC-11).

The agent_analytics table is populated exclusively by the sync_agent_analytics
PostgreSQL trigger (docs/architecture/DATABASE.md). This service NEVER inserts
or updates that table — doing so would corrupt the trigger-managed aggregates.

Coding Standard 2: async session ownership stays with the caller (get_db).
Coding Standard 3: explicit return types and parameter types throughout.
Coding Standard 6: guard clauses; max 50 lines per method.
"""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.agent import Agent
from app.models.agent_analytics import AgentAnalytics
from app.schemas.analytics import AgentAnalyticsSummary

logger = logging.getLogger(__name__)


def _compute_success_rate(total: int, successful: int) -> float:
    """Return successful / total, or 0.0 when total is zero (guard: no ZeroDivision)."""
    if total <= 0:
        return 0.0
    return round(successful / total, 4)


def _row_to_summary(agent_name: str, aa: AgentAnalytics) -> AgentAnalyticsSummary:
    """
    Map an AgentAnalytics ORM row + agent name to the response schema.

    avg_execution_time_ms is stored as DECIMAL(10,2); cast to float for JSON.
    last_run_at maps to last_executed_at in the response schema.
    """
    # Explicit None check — falsy check would coerce 0.0 (valid value) to None
    avg_ms: Optional[float] = (
        float(aa.avg_execution_time_ms) if aa.avg_execution_time_ms is not None else None
    )
    # last_run_at is Mapped[Optional[object]] in the ORM model (SQLAlchemy DateTime
    # maps to datetime at runtime; declared as object to avoid cross-dialect import
    # issues). The isinstance check is safe: the DateTime column always returns a
    # datetime instance or None from the DB driver.
    last_run: Optional[datetime] = aa.last_run_at if isinstance(aa.last_run_at, datetime) else None
    return AgentAnalyticsSummary(
        agent_id=aa.agent_id,
        agent_name=agent_name,
        total_executions=aa.total_runs,
        successful_executions=aa.successful_runs,
        failed_executions=aa.failed_runs,
        success_rate=_compute_success_rate(aa.total_runs, aa.successful_runs),
        avg_execution_time_ms=avg_ms,
        last_executed_at=last_run,
    )


class AnalyticsService:
    """
    Read-only analytics queries.

    Stateless — safe to instantiate once and reuse across requests.
    All methods accept a caller-provided AsyncSession so the session
    lifecycle is owned by the FastAPI dependency (get_db).
    """

    async def get_all_agents_stats(
        self,
        db: AsyncSession,
    ) -> list[AgentAnalyticsSummary]:
        """
        Return aggregated stats for every agent that has an analytics row.

        JOIN agent_analytics → agents to get the human-readable agent name.
        Results are sorted alphabetically by agent name for stable UI ordering.
        Returns an empty list when no analytics rows exist.
        """
        stmt = (
            sa.select(Agent.name, AgentAnalytics)
            .join(Agent, Agent.id == AgentAnalytics.agent_id)
            .order_by(Agent.name.asc())
        )
        result = await db.execute(stmt)
        rows = result.all()

        return [_row_to_summary(agent_name=str(name), aa=aa) for name, aa in rows]

    async def get_agent_stats(
        self,
        db: AsyncSession,
        agent_id: UUID,
    ) -> Optional[AgentAnalyticsSummary]:
        """
        Return aggregated stats for a single agent, or None if not found.

        Returns None (not HTTP 404) — the router translates None to 404.
        Architecture rule: no HTTP concerns in service layer.
        """
        stmt = (
            sa.select(Agent.name, AgentAnalytics)
            .join(Agent, Agent.id == AgentAnalytics.agent_id)
            .where(AgentAnalytics.agent_id == agent_id)
        )
        result = await db.execute(stmt)
        row = result.first()

        if row is None:
            return None

        agent_name: str = str(row[0])
        aa: AgentAnalytics = row[1]
        return _row_to_summary(agent_name=agent_name, aa=aa)
