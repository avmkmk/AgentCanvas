"""
FastAPI shared dependencies.

verify_api_key: enforces X-API-Key header on every protected route.
get_db: yields an async SQLAlchemy session with automatic cleanup.

Coding Standard 9: all input validated at the API boundary.
Coding Standard 2: sessions are always closed via try/finally.
"""
from __future__ import annotations

import hmac
from typing import AsyncGenerator

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

# ─── Database session factory ─────────────────────────────────────────────────

# SQLite (used in tests) does not support pool_size or max_overflow — those
# kwargs are PostgreSQL / connection-pool-specific.  We detect the dialect
# prefix and only pass the pool settings for non-SQLite databases.
# (Coding Standard 4 — explicit configuration; Coding Standard 10 — comment WHY)
_is_sqlite = settings.database_url.startswith("sqlite")

if _is_sqlite:
    # StaticPool / NullPool is the correct choice for in-memory SQLite
    _engine = create_async_engine(
        settings.database_url,
        pool_pre_ping=True,
        echo=settings.debug,
    )
else:
    _engine = create_async_engine(
        settings.database_url,
        # Connection pool sizing — avoids exhaustion under concurrent requests
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,  # Detect stale connections before use
        echo=settings.debug,  # SQL logging in debug mode only
    )

_AsyncSessionLocal = async_sessionmaker(
    bind=_engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async DB session; always close it — even on exception."""
    async with _AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# ─── API key authentication ───────────────────────────────────────────────────

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(
    api_key: str | None = Security(_api_key_header),
) -> None:
    """
    Validate the X-API-Key header.

    Raises HTTP 401 if the header is absent or incorrect.
    Timing-safe comparison is used to prevent key enumeration.
    """
    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-API-Key header is required",
        )

    # hmac.compare_digest prevents timing attacks
    if not hmac.compare_digest(api_key, settings.api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )
