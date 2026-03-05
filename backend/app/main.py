"""
AgentCanvas FastAPI application entry point.

Startup sequence:
1. Load config (fails fast if env vars are missing)
2. Mount CORS middleware
3. Register global error handlers
4. Register API routers
5. Expose /health (no auth)

Coding Standard 4: one way to start — uvicorn app.main:app
Coding Standard 8: no business logic here; delegate to routers and services.
"""
from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.api.agents import router as agents_router
from app.api.executions import router as executions_router
from app.api.flows import router as flows_router
from app.api.health import router as health_router
from app.api.memory import router as memory_router
from app.api.websocket import router as websocket_router
from app.core.config import settings
from app.middleware.error_handler import register_error_handlers

# Configure root logger — level comes from env var (Coding Standard 10)
logging.basicConfig(
    level=settings.log_level.upper(),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Factory function — makes the app testable without side effects."""
    app = FastAPI(
        title="AgentCanvas API",
        version="0.1.0",
        description="Multi-agent orchestrator — flows, HITL, memory, analytics.",
        # Disable docs in production if DEBUG is not set
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
    )

    # ─── Rate limiter ─────────────────────────────────────────────────────────
    # Shared Limiter instance — mounted on app.state so slowapi can find it.
    # Individual routers declare their own @limiter.limit() decorators.
    app.state.limiter = Limiter(key_func=get_remote_address)
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]

    # ─── CORS ────────────────────────────────────────────────────────────────
    # Origins come from ALLOWED_ORIGINS env var (comma-separated)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.get_allowed_origins_list(),
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
        # Explicit headers only — Coding Standard 9 / SECURITY.md
        allow_headers=["Content-Type", "X-API-Key"],
    )

    # ─── Error handlers ───────────────────────────────────────────────────────
    register_error_handlers(app)

    # ─── Routers ──────────────────────────────────────────────────────────────
    # Health check — no auth required
    app.include_router(health_router)

    # Flow CRUD — BA-02 / BA-03
    app.include_router(flows_router, prefix="/api/v1")

    # Agent CRUD sub-routes — BA-15
    # Routes: /api/v1/flows/{flow_id}/agents[/{agent_id}]
    app.include_router(agents_router, prefix="/api/v1")

    # Execution endpoints — BA-04 / BA-05 / BA-06
    app.include_router(executions_router, prefix="/api/v1")

    # Memory endpoints — BA-09 / BA-10
    app.include_router(memory_router, prefix="/api/v1")

    # WebSocket streaming — BA-12
    # No /api/v1 prefix — WS uses /ws/executions/{execution_id}
    app.include_router(websocket_router)

    logger.info(
        "AgentCanvas API ready — log_level=%s debug=%s",
        settings.log_level,
        settings.debug,
    )
    return app


# Module-level app instance — used by uvicorn via `uvicorn app.main:app`
app = create_app()
