"""
Unit tests for app/api/health.py — /health endpoint.

The endpoint has three observable code paths:
  1. Both postgres and redis reachable → 200, status="healthy"
  2. Postgres unreachable, redis ok → 503, status="degraded", postgres error key present
  3. Redis unreachable, postgres ok → 503, status="degraded", redis error key present

We mock _AsyncSessionLocal and aioredis.from_url so no real DB or Redis is
needed.  The test must also verify that the error message exposed to the
caller is the exception *type* only — no connection strings (security
property from the implementation comments).

Coding Standard 5: every service check result is asserted explicitly.
"""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient


# ─── Fixture: test client with health router ─────────────────────────────────

@pytest.fixture(scope="module")
def health_client() -> TestClient:
    """TestClient for the health router only — no other routes needed."""
    from fastapi import FastAPI
    from app.api.health import router

    app = FastAPI()
    app.include_router(router)
    return TestClient(app, raise_server_exceptions=False)


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _mock_ok_session():
    """Return a context-manager mock that simulates a healthy postgres session."""
    session = AsyncMock()
    session.execute = AsyncMock(return_value=None)
    cm = MagicMock()
    cm.__aenter__ = AsyncMock(return_value=session)
    cm.__aexit__ = AsyncMock(return_value=False)
    return cm


def _mock_ok_redis():
    """Return a context-manager mock that simulates a reachable redis client."""
    client = AsyncMock()
    client.ping = AsyncMock(return_value=True)
    cm = MagicMock()
    cm.__aenter__ = AsyncMock(return_value=client)
    cm.__aexit__ = AsyncMock(return_value=False)
    return cm


# ─── Tests ────────────────────────────────────────────────────────────────────

class TestHealthEndpoint:

    def test_healthy_when_postgres_and_redis_ok(self, health_client: TestClient) -> None:
        with (
            patch(
                "app.api.health._AsyncSessionLocal",
                return_value=_mock_ok_session(),
            ),
            patch(
                "app.api.health.aioredis.from_url",
                return_value=_mock_ok_redis(),
            ),
        ):
            response = health_client.get("/health")

        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "healthy"
        assert body["checks"]["postgres"] == "ok"
        assert body["checks"]["redis"] == "ok"
        assert "latency_ms" in body

    def test_degraded_when_postgres_fails(self, health_client: TestClient) -> None:
        bad_session_cm = MagicMock()
        bad_session_cm.__aenter__ = AsyncMock(
            side_effect=ConnectionRefusedError("pg down")
        )
        bad_session_cm.__aexit__ = AsyncMock(return_value=False)

        with (
            patch(
                "app.api.health._AsyncSessionLocal",
                return_value=bad_session_cm,
            ),
            patch(
                "app.api.health.aioredis.from_url",
                return_value=_mock_ok_redis(),
            ),
        ):
            response = health_client.get("/health")

        assert response.status_code == 503
        body = response.json()
        assert body["status"] == "degraded"
        # Error message must contain exception type only — not connection string
        assert body["checks"]["postgres"].startswith("error:")
        assert "ConnectionRefusedError" in body["checks"]["postgres"]
        assert body["checks"]["redis"] == "ok"

    def test_degraded_when_redis_fails(self, health_client: TestClient) -> None:
        bad_redis_cm = MagicMock()
        bad_redis_cm.__aenter__ = AsyncMock(
            side_effect=ConnectionRefusedError("redis down")
        )
        bad_redis_cm.__aexit__ = AsyncMock(return_value=False)

        with (
            patch(
                "app.api.health._AsyncSessionLocal",
                return_value=_mock_ok_session(),
            ),
            patch(
                "app.api.health.aioredis.from_url",
                return_value=bad_redis_cm,
            ),
        ):
            response = health_client.get("/health")

        assert response.status_code == 503
        body = response.json()
        assert body["status"] == "degraded"
        assert body["checks"]["postgres"] == "ok"
        assert body["checks"]["redis"].startswith("error:")
        assert "ConnectionRefusedError" in body["checks"]["redis"]

    def test_degraded_when_both_services_fail(self, health_client: TestClient) -> None:
        bad_session_cm = MagicMock()
        bad_session_cm.__aenter__ = AsyncMock(
            side_effect=OSError("pg unavailable")
        )
        bad_session_cm.__aexit__ = AsyncMock(return_value=False)

        bad_redis_cm = MagicMock()
        bad_redis_cm.__aenter__ = AsyncMock(
            side_effect=OSError("redis unavailable")
        )
        bad_redis_cm.__aexit__ = AsyncMock(return_value=False)

        with (
            patch(
                "app.api.health._AsyncSessionLocal",
                return_value=bad_session_cm,
            ),
            patch(
                "app.api.health.aioredis.from_url",
                return_value=bad_redis_cm,
            ),
        ):
            response = health_client.get("/health")

        assert response.status_code == 503
        body = response.json()
        assert body["status"] == "degraded"
        assert body["checks"]["postgres"].startswith("error:")
        assert body["checks"]["redis"].startswith("error:")

    def test_response_never_exposes_connection_string_in_error(
        self, health_client: TestClient
    ) -> None:
        """
        Security property: error messages must not leak internal hostnames or
        credentials.  The implementation logs only exc_type — verify that
        a fictional connection string cannot appear in the response body.
        """
        connection_string = "postgresql://admin:s3cr3t@internal-host:5432/orchestrator"

        class _LeakyError(Exception):
            def __str__(self) -> str:
                return connection_string

        bad_session_cm = MagicMock()
        bad_session_cm.__aenter__ = AsyncMock(side_effect=_LeakyError())
        bad_session_cm.__aexit__ = AsyncMock(return_value=False)

        with (
            patch(
                "app.api.health._AsyncSessionLocal",
                return_value=bad_session_cm,
            ),
            patch(
                "app.api.health.aioredis.from_url",
                return_value=_mock_ok_redis(),
            ),
        ):
            response = health_client.get("/health")

        body_text = response.text
        assert "s3cr3t" not in body_text
        assert "internal-host" not in body_text
        assert "admin" not in body_text

    def test_latency_ms_is_non_negative_number(self, health_client: TestClient) -> None:
        with (
            patch(
                "app.api.health._AsyncSessionLocal",
                return_value=_mock_ok_session(),
            ),
            patch(
                "app.api.health.aioredis.from_url",
                return_value=_mock_ok_redis(),
            ),
        ):
            response = health_client.get("/health")

        latency = response.json()["latency_ms"]
        assert isinstance(latency, (int, float))
        assert latency >= 0
