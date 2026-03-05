"""
Integration tests for the Flow CRUD API — BA-02.

These tests exercise the full HTTP stack: router → service → DB (SQLite
in-memory via db_session).  They use the async_client fixture from conftest.py
and the test API key from the _TEST_ENV overrides.

Import guard: the flows router and FlowService are being written in BA-02.
Until they are registered in main.py, these tests are collected but each
test will return 404 from the still-unregistered routes.  We skip the suite
at module level if the router import is unavailable so CI does not block M1.

Coding Standard 5: every request asserts a specific HTTP status, not just
a truthy response.
Coding Standard 9: dangerous-name and size-limit paths are always tested.
"""
from __future__ import annotations

import uuid

import pytest
from httpx import AsyncClient

# ─── Availability guard ───────────────────────────────────────────────────────
# The flows router lands with BA-02.  Until then the tests are collected but
# skipped so the test run stays green.

try:
    from app.api import flows as _flows_module  # type: ignore[import]  # noqa: F401

    _ROUTER_AVAILABLE = True
except ImportError:
    _ROUTER_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not _ROUTER_AVAILABLE,
    reason="Flows router (BA-02) not yet registered — tests activate once the module lands",
)

# ─── Constants ────────────────────────────────────────────────────────────────

# Must match _TEST_ENV["API_KEY"] in conftest.py
_API_KEY = "test-api-key-for-unit-tests"
_AUTH_HEADERS = {"X-API-Key": _API_KEY}
_VALID_PAYLOAD = {"name": "test-flow", "description": "integration test flow"}

# ─── Helpers ──────────────────────────────────────────────────────────────────


async def _create_flow(client: AsyncClient, **overrides: object) -> dict:  # type: ignore[type-arg]
    """POST a valid flow and return the parsed JSON body."""
    payload = {**_VALID_PAYLOAD, **overrides}
    response = await client.post(
        "/api/v1/flows",
        json=payload,
        headers=_AUTH_HEADERS,
    )
    assert response.status_code == 201, (
        f"Helper _create_flow expected 201, got {response.status_code}: {response.text}"
    )
    return response.json()


# ─── POST /api/v1/flows ───────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_flow_returns_201(async_client: AsyncClient) -> None:
    """Happy path: valid payload with auth must return HTTP 201."""
    response = await async_client.post(
        "/api/v1/flows",
        json=_VALID_PAYLOAD,
        headers=_AUTH_HEADERS,
    )
    assert response.status_code == 201
    body = response.json()
    assert "id" in body, "Response must contain an 'id' field"
    assert body["name"] == "test-flow"
    assert body["is_active"] is True


@pytest.mark.asyncio
async def test_create_flow_requires_api_key(async_client: AsyncClient) -> None:
    """Request without X-API-Key must be rejected with HTTP 401."""
    response = await async_client.post(
        "/api/v1/flows",
        json=_VALID_PAYLOAD,
        # Deliberately omitting _AUTH_HEADERS
    )
    assert response.status_code == 401, (
        "Missing API key must return 401, not any other status"
    )


@pytest.mark.asyncio
async def test_create_flow_rejects_dangerous_name(async_client: AsyncClient) -> None:
    """Name containing XSS payload must be rejected with HTTP 422."""
    response = await async_client.post(
        "/api/v1/flows",
        json={"name": "<script>alert('xss')</script>", "description": "evil"},
        headers=_AUTH_HEADERS,
    )
    assert response.status_code == 422, (
        "XSS payload in name must trigger schema validation → 422"
    )


@pytest.mark.asyncio
async def test_create_flow_rejects_empty_name(async_client: AsyncClient) -> None:
    """Empty string name must be rejected with HTTP 422 (min_length=1)."""
    response = await async_client.post(
        "/api/v1/flows",
        json={"name": "", "description": "no name"},
        headers=_AUTH_HEADERS,
    )
    assert response.status_code == 422, (
        "Empty name must fail Pydantic min_length validation → 422"
    )


# ─── GET /api/v1/flows/{flow_id} ─────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_flow_returns_404_for_unknown(async_client: AsyncClient) -> None:
    """GET on a UUID that does not exist must return HTTP 404."""
    unknown_id = uuid.uuid4()
    response = await async_client.get(
        f"/api/v1/flows/{unknown_id}",
        headers=_AUTH_HEADERS,
    )
    assert response.status_code == 404, (
        "Non-existent flow_id must return 404"
    )


@pytest.mark.asyncio
async def test_get_flow_returns_flow_when_found(async_client: AsyncClient) -> None:
    """GET on an existing flow id must return the flow with HTTP 200."""
    created = await _create_flow(async_client)
    flow_id = created["id"]

    response = await async_client.get(
        f"/api/v1/flows/{flow_id}",
        headers=_AUTH_HEADERS,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == flow_id
    assert body["name"] == "test-flow"


# ─── GET /api/v1/flows ────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_flows_returns_paginated_response(async_client: AsyncClient) -> None:
    """
    GET /api/v1/flows must return a FlowListResponse with 'items' and 'total'.
    The structure must be stable regardless of how many flows exist.
    """
    response = await async_client.get(
        "/api/v1/flows?page=1&page_size=10",
        headers=_AUTH_HEADERS,
    )
    assert response.status_code == 200
    body = response.json()
    assert "items" in body, "List response must contain 'items' key"
    assert "total" in body, "List response must contain 'total' key"
    assert isinstance(body["items"], list)
    assert isinstance(body["total"], int)


@pytest.mark.asyncio
async def test_list_flows_page_size_limit(async_client: AsyncClient) -> None:
    """
    page_size=200 exceeds the API maximum of 100 and must return HTTP 422.
    This prevents memory exhaustion via oversized result sets.
    """
    response = await async_client.get(
        "/api/v1/flows?page=1&page_size=200",
        headers=_AUTH_HEADERS,
    )
    assert response.status_code == 422, (
        "page_size > 100 must be rejected with 422"
    )


# ─── PATCH /api/v1/flows/{flow_id} ───────────────────────────────────────────


@pytest.mark.asyncio
async def test_update_flow_partial_update(async_client: AsyncClient) -> None:
    """
    PATCH with only 'name' must update the name and leave other fields intact.
    Verifies exclude_unset PATCH semantics at the HTTP level.
    """
    created = await _create_flow(async_client, description="original description")
    flow_id = created["id"]

    response = await async_client.patch(
        f"/api/v1/flows/{flow_id}",
        json={"name": "updated-name"},
        headers=_AUTH_HEADERS,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "updated-name", "Name must reflect the PATCH value"
    assert body["description"] == "original description", (
        "Unpatched description must remain unchanged"
    )


@pytest.mark.asyncio
async def test_update_flow_returns_404_for_unknown(async_client: AsyncClient) -> None:
    """PATCH on a non-existent flow_id must return HTTP 404."""
    unknown_id = uuid.uuid4()
    response = await async_client.patch(
        f"/api/v1/flows/{unknown_id}",
        json={"name": "irrelevant"},
        headers=_AUTH_HEADERS,
    )
    assert response.status_code == 404


# ─── DELETE /api/v1/flows/{flow_id} ──────────────────────────────────────────


@pytest.mark.asyncio
async def test_delete_flow_returns_204(async_client: AsyncClient) -> None:
    """DELETE on an existing flow must return HTTP 204 No Content."""
    created = await _create_flow(async_client)
    flow_id = created["id"]

    response = await async_client.delete(
        f"/api/v1/flows/{flow_id}",
        headers=_AUTH_HEADERS,
    )
    assert response.status_code == 204, (
        "Successful delete must return 204 No Content"
    )
    # 204 must have no body
    assert response.content == b"", "204 response must have empty body"


@pytest.mark.asyncio
async def test_delete_flow_returns_404_for_unknown(async_client: AsyncClient) -> None:
    """DELETE on a non-existent flow_id must return HTTP 404."""
    unknown_id = uuid.uuid4()
    response = await async_client.delete(
        f"/api/v1/flows/{unknown_id}",
        headers=_AUTH_HEADERS,
    )
    assert response.status_code == 404, (
        "Non-existent flow_id must return 404 on DELETE"
    )
