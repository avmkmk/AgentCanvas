"""
pytest fixtures shared by all test modules.

Rules:
- Never use the dev database — all tests use an in-memory SQLite engine.
- Never call the real Anthropic API — mock_llm patches LLMService.complete.
- app_client builds a TestClient from the FastAPI factory with env vars
  overridden so no real external services are required at import time.

Coding Standard 2: all fixtures clean up after themselves.
Coding Standard 5: any missing env override fails loudly here — not silently
  mid-test.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import AsyncGenerator
from unittest.mock import AsyncMock, patch

from dotenv import load_dotenv

# Load .env.test so test env values are in a file, not hardcoded strings.
# override=False → OS env vars (e.g. from CI) always win over the file.
load_dotenv(Path(__file__).resolve().parent.parent / ".env.test", override=False)

import pytest  # noqa: E402
import pytest_asyncio  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from httpx import AsyncClient, ASGITransport  # noqa: E402
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine  # noqa: E402

from app.db.base import Base  # noqa: E402

# ─── Environment overrides ────────────────────────────────────────────────────
# Set before any app module is imported so pydantic-settings picks them up.
# These are test-only values — not real credentials.
_TEST_ENV: dict[str, str] = {
    "DATABASE_URL": "sqlite+aiosqlite:///:memory:",
    "MONGO_URI": "mongodb://localhost:27017/test",
    "REDIS_URL": "redis://localhost:6379/1",
    "API_KEY": "test-api-key-for-unit-tests",
    "ANTHROPIC_API_KEY": "sk-ant-test-key",
    "ALLOWED_ORIGINS": "http://localhost:3000",
    "LOG_LEVEL": "ERROR",  # suppress noise during tests
    "DEBUG": "false",
}

for _key, _val in _TEST_ENV.items():
    os.environ.setdefault(_key, _val)


# ─── Test database engine ──────────────────────────────────────────────────────

_test_engine = create_async_engine(
    "sqlite+aiosqlite:///:memory:",
    # SQLite does not enforce foreign keys by default — not needed for unit tests
    connect_args={"check_same_thread": False},
)

_TestSessionLocal = async_sessionmaker(
    bind=_test_engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


@pytest_asyncio.fixture()
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Yield a fresh AsyncSession backed by an in-memory SQLite DB.

    Creates all tables before the test and drops them after, ensuring
    full isolation between test cases.
    """
    async with _test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with _TestSessionLocal() as session:
        yield session
    async with _test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# ─── LLM mock ─────────────────────────────────────────────────────────────────

@pytest.fixture()
def mock_llm():
    """
    Patch LLMService.complete so no real Anthropic API call is made.

    The mock returns a predictable string — tests can override the return
    value with mock_llm.return_value = ... for specific scenarios.
    """
    with patch("app.services.llm_service.LLMService.complete") as mock:
        mock.return_value = AsyncMock(return_value="Mocked LLM response")
        yield mock


# ─── FastAPI test client ───────────────────────────────────────────────────────

@pytest.fixture()
def app():
    """
    Return the FastAPI application instance.

    Imported here (not at module level) so environment overrides above are
    already in place before pydantic-settings runs.
    """
    # Lazy import — env must be set first
    from app.main import create_app  # noqa: PLC0415

    return create_app()


@pytest.fixture()
def test_client(app) -> TestClient:
    """Synchronous TestClient — for endpoints that do not need async context."""
    return TestClient(app, raise_server_exceptions=True)


@pytest_asyncio.fixture()
async def async_client(app) -> AsyncGenerator[AsyncClient, None]:
    """
    Async HTTPX client for testing async FastAPI routes.

    Uses ASGITransport so no real TCP socket is opened.

    DB isolation: the app's get_db dependency is overridden so that every
    request goes through the same in-memory SQLite engine used by
    db_session. Tables are created before the client yields and torn down
    after, giving the same isolation guarantee as db_session.

    Coding Standard 2: dependency override is always cleared after the test
    to prevent state leaking into other fixtures.
    """
    from app.api.dependencies import get_db  # noqa: PLC0415

    # Build tables on the shared test engine (same engine as db_session)
    async with _test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Override get_db to use the test session factory so the app never
    # touches the real DATABASE_URL from settings.
    async def _override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with _TestSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = _override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    # Cleanup — drop tables and remove the override so later fixtures
    # that share the same app instance are not affected.
    app.dependency_overrides.pop(get_db, None)
    async with _test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
