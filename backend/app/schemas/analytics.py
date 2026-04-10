"""
Pydantic v2 response schemas for analytics endpoints (BA-11).

AgentAnalyticsResponse: legacy per-agent row schema (unchanged).
AgentAnalyticsSummary: M5 summary schema used by the analytics router.
AgentAnalyticsListResponse: list wrapper for GET /analytics/agents.

Read-only — the agent_analytics table is written exclusively by the
sync_agent_analytics PostgreSQL trigger (docs/architecture/DATABASE.md).
Coding Standard 3: all fields explicitly typed.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AgentAnalyticsResponse(BaseModel):
    """Legacy schema — kept for backwards compat with existing imports."""
    id: UUID
    agent_id: UUID
    total_runs: int
    successful_runs: int
    failed_runs: int
    avg_execution_time_ms: float
    min_execution_time_ms: Optional[int]
    max_execution_time_ms: Optional[int]
    total_llm_calls: int
    total_hitl_reviews: int
    last_run_at: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class AgentAnalyticsSummary(BaseModel):
    """
    Aggregated execution stats for a single agent — used by GET /analytics/agents.

    success_rate is computed by AnalyticsService (0.0 when total_executions == 0).
    avg_execution_time_ms and last_executed_at are None when the agent has
    never been executed.
    """

    agent_id: UUID
    agent_name: str
    total_executions: int
    successful_executions: int
    failed_executions: int
    # Computed field — not stored in DB; derived in AnalyticsService
    success_rate: float
    # None until at least one execution has completed
    avg_execution_time_ms: Optional[float]
    last_executed_at: Optional[datetime]

    # from_attributes=True: allows construction from SQLAlchemy row objects
    model_config = ConfigDict(from_attributes=True)


class AgentAnalyticsListResponse(BaseModel):
    """Response wrapper for GET /analytics/agents."""

    items: list[AgentAnalyticsSummary]
    total: int
