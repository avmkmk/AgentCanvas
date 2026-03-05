"""
Health check router — /health endpoint.

No auth required — used by Docker health checks and load balancers.
Checks both PostgreSQL and Redis connectivity.
Coding Standard 5: every check result is explicit — no silent failures.
Coding Standard 2: Redis client always closed via async context manager.
"""
from __future__ import annotations

import logging
import time

import redis.asyncio as aioredis
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

# Reuse the shared engine from dependencies — avoids a second connection pool
# and eliminates the module-level resource leak from an unmanaged second engine.
from app.api.dependencies import _AsyncSessionLocal
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


@router.get("/health", include_in_schema=False)
async def health_check() -> JSONResponse:
    """
    Returns 200 if all downstream services are reachable, 503 otherwise.
    Response body includes per-service status (generic messages — no internal
    hostnames or connection strings exposed to callers; full detail is logged).
    """
    start = time.monotonic()
    checks: dict[str, str] = {}
    all_ok = True

    # ─── PostgreSQL ────────────────────────────────────────────────────────
    try:
        async with _AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        checks["postgres"] = "ok"
    except Exception as exc:  # noqa: BLE001 — health check must not crash
        # Log full detail server-side; return only the exception type to the
        # caller to avoid leaking connection strings (Security — info disclosure).
        logger.error("PostgreSQL health check failed: %s", exc)
        checks["postgres"] = f"error: {type(exc).__name__}"
        all_ok = False

    # ─── Redis ─────────────────────────────────────────────────────────────
    # Use async context manager so the connection is closed even if ping raises.
    try:
        async with aioredis.from_url(
            settings.redis_url, socket_timeout=2
        ) as client:
            await client.ping()
        checks["redis"] = "ok"
    except Exception as exc:  # noqa: BLE001
        logger.error("Redis health check failed: %s", exc)
        checks["redis"] = f"error: {type(exc).__name__}"
        all_ok = False

    elapsed_ms = round((time.monotonic() - start) * 1000, 1)

    body = {
        "status": "healthy" if all_ok else "degraded",
        "checks": checks,
        "latency_ms": elapsed_ms,
    }

    http_status = status.HTTP_200_OK if all_ok else status.HTTP_503_SERVICE_UNAVAILABLE
    return JSONResponse(content=body, status_code=http_status)
