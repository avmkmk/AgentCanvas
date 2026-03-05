"""
Pydantic v2 response schema for AgentAnalytics.

Read-only — the analytics table is written exclusively by the DB trigger.
avg_execution_time_ms is a float because the DB stores DECIMAL(10,2).
"""
from __future__ import annotations

from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class AgentAnalyticsResponse(BaseModel):
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

    model_config = {"from_attributes": True}
