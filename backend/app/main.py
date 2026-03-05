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

from app.api.agents import router as agents_router
from app.api.flows import router as flows_router
from app.api.health import router as health_router
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

    # ─── CORS ────────────────────────────────────────────────────────────────
    # Origins come from ALLOWED_ORIGINS env var (comma-separated)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.get_allowed_origins_list(),
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "DELETE"],
        # Explicit headers only — Coding Standard 9 / SECURITY.md
        allow_headers=["Content-Type", "X-API-Key"],
    )

    # ─── Error handlers ───────────────────────────────────────────────────────
    register_error_handlers(app)

    # ─── Routers ──────────────────────────────────────────────────────────────
    # Health check — no auth required
    app.include_router(health_router)

    # Flow CRUD — BA-02 / BA-03
    # verify_api_key is declared on each route handler, not at router level,
    # so the dependency is explicit and visible in OpenAPI docs.
    app.include_router(flows_router, prefix="/api/v1")

    # Agent CRUD sub-routes — BA-15
    # Routes: /api/v1/flows/{flow_id}/agents[/{agent_id}]
    app.include_router(agents_router, prefix="/api/v1")

    # Future routers (uncomment as implemented):
    # app.include_router(executions_router, prefix="/api/v1")
    # app.include_router(hitl_router, prefix="/api/v1")
    # app.include_router(analytics_router, prefix="/api/v1")

    logger.info(
        "AgentCanvas API ready — log_level=%s debug=%s",
        settings.log_level,
        settings.debug,
    )
    return app


# Module-level app instance — used by uvicorn via `uvicorn app.main:app`
app = create_app()
