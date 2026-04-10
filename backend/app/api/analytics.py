"""
Analytics router — BA-11 (agent stats endpoints).

Thin router: validate path param → call AnalyticsService → return response.
No SQL queries here (ARCHITECTURE.md layer rule: no business logic in routers).

Security:
- verify_api_key on every route (SECURITY.md)
- No LLM calls — rate limiting not required for this router
"""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db, verify_api_key
from app.schemas.analytics import AgentAnalyticsListResponse, AgentAnalyticsSummary
from app.services.analytics_service import AnalyticsService

router = APIRouter(tags=["analytics"])

# Stateless singleton — no instance state; safe to share across requests
_analytics_service = AnalyticsService()


@router.get(
    "/agents",
    response_model=AgentAnalyticsListResponse,
    summary="List aggregated stats for all agents",
    dependencies=[Depends(verify_api_key)],
)
async def list_agent_stats(
    db: AsyncSession = Depends(get_db),
) -> AgentAnalyticsListResponse:
    """
    Return execution statistics for every agent that has been executed at least once.

    Results are sorted alphabetically by agent name.
    Returns an empty list (not 404) when no analytics data exists yet.
    """
    summaries = await _analytics_service.get_all_agents_stats(db=db)
    return AgentAnalyticsListResponse(items=summaries, total=len(summaries))


@router.get(
    "/agents/{agent_id}",
    response_model=AgentAnalyticsSummary,
    summary="Get aggregated stats for a single agent",
    dependencies=[Depends(verify_api_key)],
)
async def get_agent_stats(
    agent_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> AgentAnalyticsSummary:
    """
    Return execution statistics for a single agent.

    Returns 404 if the agent has no analytics record (never executed or does not exist).
    """
    summary = await _analytics_service.get_agent_stats(db=db, agent_id=agent_id)
    if summary is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No analytics found for the specified agent",
        )
    return summary
