"""
Unit tests for app/api/dependencies.py — verify_api_key security guard.

verify_api_key is the only thing standing between the public internet and
every protected endpoint.  Tests cover:
  - Missing header → 401 "X-API-Key header is required"
  - Wrong key → 401 "Invalid API key"
  - Correct key → request allowed through (no exception raised)

We test through the FastAPI TestClient rather than calling verify_api_key
directly because the dependency is wired as a FastAPI Security dependency;
testing it in isolation would not exercise the Security() extraction logic.

A minimal router is registered on a fresh app instance so the test does not
depend on the existence of any real route.

Coding Standard 3: every assertion is explicit — no implicit truthiness checks.
"""
from __future__ import annotations

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from app.api.dependencies import verify_api_key
from app.core.config import settings


# ─── Minimal test app ─────────────────────────────────────────────────────────

def _build_protected_app() -> FastAPI:
    """
    Tiny FastAPI app with one protected route used only in tests.

    Separate from the real app factory to avoid side-effects.
    """
    app = FastAPI()

    @app.get("/protected", dependencies=[Depends(verify_api_key)])
    async def _protected_route() -> dict:
        return {"ok": True}

    return app


@pytest.fixture(scope="module")
def protected_client() -> TestClient:
    return TestClient(_build_protected_app(), raise_server_exceptions=False)


# ─── Tests ────────────────────────────────────────────────────────────────────

class TestVerifyApiKey:
    """All three branches of verify_api_key must behave exactly as specified."""

    def test_missing_header_returns_401(self, protected_client: TestClient) -> None:
        response = protected_client.get("/protected")
        assert response.status_code == 401
        body = response.json()
        assert body["detail"] == "X-API-Key header is required"

    def test_wrong_key_returns_401(self, protected_client: TestClient) -> None:
        response = protected_client.get(
            "/protected", headers={"X-API-Key": "definitely-wrong-key"}
        )
        assert response.status_code == 401
        body = response.json()
        assert body["detail"] == "Invalid API key"

    def test_correct_key_allows_request(self, protected_client: TestClient) -> None:
        response = protected_client.get(
            "/protected", headers={"X-API-Key": settings.api_key}
        )
        assert response.status_code == 200
        assert response.json() == {"ok": True}

    def test_empty_string_header_returns_401(self, protected_client: TestClient) -> None:
        # An empty X-API-Key header is present but incorrect — must be rejected
        response = protected_client.get(
            "/protected", headers={"X-API-Key": ""}
        )
        # FastAPI's APIKeyHeader with auto_error=False returns None for empty
        # strings on some versions; the dependency raises 401 either way.
        assert response.status_code == 401

    def test_key_comparison_is_case_sensitive(self, protected_client: TestClient) -> None:
        # API keys are case-sensitive — uppercase of the correct key must fail
        upper_key = settings.api_key.upper()
        if upper_key == settings.api_key:
            pytest.skip("Test API key is already all-uppercase — skip case check")
        response = protected_client.get(
            "/protected", headers={"X-API-Key": upper_key}
        )
        assert response.status_code == 401
