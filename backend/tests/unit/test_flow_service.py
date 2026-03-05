"""
Unit tests for FlowService — mocked AsyncSession.

These tests do NOT rely on the SQLite db_session fixture because FlowService
uses SQLAlchemy select() / scalars() patterns that behave differently in
SQLite vs PostgreSQL.  Instead, every AsyncSession method is replaced with
an AsyncMock so we test only the service logic, not the ORM driver.

Coding Standard 7: every function under test has a happy path and at least
one failure path.
Coding Standard 5: no bare except; each test asserts a specific condition.
"""
from __future__ import annotations

import uuid
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.schemas.flow import FlowCreate, FlowUpdate

# FlowService is not yet implemented (BA-02 is in progress).
# We import conditionally so collection does not fail before the service
# module exists.  Once the module lands, the import guard is removed.
try:
    from app.services.flow_service import FlowService  # type: ignore[import]

    _SERVICE_AVAILABLE = True
except ImportError:
    FlowService = None  # type: ignore[assignment,misc]
    _SERVICE_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not _SERVICE_AVAILABLE,
    reason="FlowService (BA-02) not yet implemented — tests will activate once the module lands",
)


# ─── Fixtures ─────────────────────────────────────────────────────────────────


@pytest.fixture()
def service() -> "FlowService":  # type: ignore[type-arg]
    """Return a fresh FlowService instance."""
    return FlowService()  # type: ignore[misc]


@pytest.fixture()
def mock_db() -> AsyncMock:
    """Async mock for SQLAlchemy AsyncSession."""
    db: AsyncMock = AsyncMock()
    db.execute = AsyncMock()
    db.add = MagicMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    db.delete = AsyncMock()
    return db


def _make_mock_flow(
    name: str = "test-flow",
    description: str | None = None,
    flow_config: dict[str, Any] | None = None,
) -> MagicMock:
    """Return a MagicMock that looks like a Flow ORM instance."""
    flow = MagicMock()
    flow.id = uuid.uuid4()
    flow.name = name
    flow.description = description
    flow.flow_config = flow_config if flow_config is not None else {"nodes": [], "edges": []}
    flow.is_active = True
    return flow


def _make_scalar_result(row: Any) -> MagicMock:
    """Wrap a value so db.execute(...).scalar_one_or_none() returns it."""
    result = MagicMock()
    result.scalar_one_or_none = MagicMock(return_value=row)
    return result


def _make_scalars_result(rows: list[Any], total: int) -> tuple[MagicMock, MagicMock]:
    """
    Return two MagicMocks that simulate the two execute() calls in list_flows:
    first for the count query, second for the rows query.
    """
    count_result = MagicMock()
    count_result.scalar_one = MagicMock(return_value=total)

    rows_result = MagicMock()
    scalars_mock = MagicMock()
    scalars_mock.all = MagicMock(return_value=rows)
    rows_result.scalars = MagicMock(return_value=scalars_mock)

    return count_result, rows_result


# ─── create_flow ──────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_flow_sets_default_flow_config(
    service: "FlowService",  # type: ignore[type-arg]
    mock_db: AsyncMock,
) -> None:
    """
    When FlowCreate.flow_config is an empty dict (the schema default),
    the service must store {"nodes": [], "edges": []} so the canvas
    renderer never receives a structurally incomplete config.

    This guards issue #carry-forward-4 from MEMORY.md.
    """
    payload = FlowCreate(name="empty-config-flow")

    async def _fake_refresh(obj: Any) -> None:
        # Simulate DB populating the id / timestamps
        obj.id = uuid.uuid4()

    mock_db.refresh.side_effect = _fake_refresh

    await service.create_flow(db=mock_db, data=payload)

    # Service must have called db.add() with an object whose flow_config
    # is the normalised default, not an empty dict.
    added_obj = mock_db.add.call_args[0][0]
    assert added_obj.flow_config == {"nodes": [], "edges": []}, (
        "Service must normalise empty flow_config to {'nodes': [], 'edges': []}"
    )
    mock_db.commit.assert_awaited_once()
    mock_db.refresh.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_flow_with_explicit_flow_config(
    service: "FlowService",  # type: ignore[type-arg]
    mock_db: AsyncMock,
) -> None:
    """
    When the caller supplies a flow_config, the service must preserve it
    exactly — not overwrite it with the default.
    """
    custom_config: dict[str, Any] = {
        "nodes": [{"id": "node-1", "type": "agent"}],
        "edges": [{"id": "edge-1", "source": "node-1", "target": "node-2"}],
    }
    payload = FlowCreate(name="explicit-config-flow", flow_config=custom_config)

    await service.create_flow(db=mock_db, data=payload)

    added_obj = mock_db.add.call_args[0][0]
    assert added_obj.flow_config == custom_config, (
        "Explicitly provided flow_config must not be overwritten"
    )


# ─── get_flow ─────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_flow_returns_none_for_unknown_id(
    service: "FlowService",  # type: ignore[type-arg]
    mock_db: AsyncMock,
) -> None:
    """
    get_flow(unknown_id) must return None, not raise an exception.
    The router converts None → HTTP 404.
    """
    unknown_id = uuid.uuid4()
    mock_db.execute.return_value = _make_scalar_result(None)

    result = await service.get_flow(db=mock_db, flow_id=unknown_id)

    assert result is None, "Unknown flow_id must return None"


@pytest.mark.asyncio
async def test_get_flow_returns_flow_when_found(
    service: "FlowService",  # type: ignore[type-arg]
    mock_db: AsyncMock,
) -> None:
    """get_flow with a valid id must return the flow object from the DB."""
    mock_flow = _make_mock_flow(name="existing-flow")
    mock_db.execute.return_value = _make_scalar_result(mock_flow)

    result = await service.get_flow(db=mock_db, flow_id=mock_flow.id)

    assert result is mock_flow, "get_flow must return the ORM object from the DB"


# ─── list_flows ───────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_flows_returns_empty_list_when_no_data(
    service: "FlowService",  # type: ignore[type-arg]
    mock_db: AsyncMock,
) -> None:
    """list_flows with no rows in the DB must return ([], 0)."""
    count_result, rows_result = _make_scalars_result(rows=[], total=0)
    mock_db.execute.side_effect = [count_result, rows_result]

    flows, total = await service.list_flows(db=mock_db, page=1, page_size=10)

    assert flows == [], "Empty table must return an empty list"
    assert total == 0, "Empty table must return total=0"


@pytest.mark.asyncio
async def test_list_flows_page_two_makes_two_db_calls(
    service: "FlowService",  # type: ignore[type-arg]
    mock_db: AsyncMock,
) -> None:
    """
    list_flows makes exactly 2 execute calls: one for count, one for data.

    We verify the observable output (call count, total, items) rather than
    inspecting private SQLAlchemy internals such as _offset, which are not
    part of the public API and break across patch releases.
    """
    count_result = MagicMock()
    count_result.scalar_one.return_value = 25

    data_result = MagicMock()
    data_result.scalars.return_value.all.return_value = []

    mock_db.execute.side_effect = [count_result, data_result]

    items, total = await service.list_flows(mock_db, page=2, page_size=10)

    assert mock_db.execute.call_count == 2, (
        "list_flows must execute exactly 2 queries: count + rows"
    )
    assert total == 25, "total must reflect the count query result"
    assert items == [], "items must reflect the data query result"


# ─── update_flow ──────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_update_flow_applies_only_provided_fields(
    service: "FlowService",  # type: ignore[type-arg]
    mock_db: AsyncMock,
) -> None:
    """
    PATCH semantics: only fields that are explicitly set in FlowUpdate must
    be applied.  Fields left at None / unset must not overwrite the existing
    DB values.

    This uses Pydantic's exclude_unset=True behaviour.
    """
    original_description = "original description"
    mock_flow = _make_mock_flow(name="old-name", description=original_description)
    mock_db.execute.return_value = _make_scalar_result(mock_flow)

    # Only updating the name; description is left unset
    update_payload = FlowUpdate(name="new-name")

    result = await service.update_flow(
        db=mock_db, flow_id=mock_flow.id, data=update_payload
    )

    assert result is not None
    # Name must have been updated
    assert result.name == "new-name", "Provided field must be applied"
    # Description must be untouched
    assert result.description == original_description, (
        "Unset fields must not be overwritten (exclude_unset=True)"
    )
    mock_db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_flow_returns_none_for_unknown_id(
    service: "FlowService",  # type: ignore[type-arg]
    mock_db: AsyncMock,
) -> None:
    """update_flow for a non-existent id must return None, not raise."""
    mock_db.execute.return_value = _make_scalar_result(None)

    result = await service.update_flow(
        db=mock_db,
        flow_id=uuid.uuid4(),
        data=FlowUpdate(name="irrelevant"),
    )

    assert result is None, "Unknown flow_id must return None from update_flow"
    mock_db.commit.assert_not_awaited()


# ─── delete_flow ──────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_delete_flow_returns_true_when_found(
    service: "FlowService",  # type: ignore[type-arg]
    mock_db: AsyncMock,
) -> None:
    """
    delete_flow must return True when the flow exists.

    delete_flow is a soft delete: it sets is_active=False and commits
    rather than issuing a DB DELETE statement.  The DB CASCADE on hard
    delete is intentionally not triggered — soft-deleted flows can be
    recovered if needed.
    """
    mock_flow = _make_mock_flow()
    mock_db.execute.return_value = _make_scalar_result(mock_flow)

    deleted = await service.delete_flow(db=mock_db, flow_id=mock_flow.id)

    assert deleted is True, "delete_flow must return True on successful soft-delete"
    # Soft delete: is_active flag must be set to False
    assert mock_flow.is_active is False, (
        "Soft delete must set is_active=False on the flow object"
    )
    # Soft delete commits but never calls db.delete
    mock_db.commit.assert_awaited_once()
    mock_db.delete.assert_not_awaited()


@pytest.mark.asyncio
async def test_delete_flow_returns_false_when_not_found(
    service: "FlowService",  # type: ignore[type-arg]
    mock_db: AsyncMock,
) -> None:
    """delete_flow must return False when the flow does not exist."""
    mock_db.execute.return_value = _make_scalar_result(None)

    deleted = await service.delete_flow(db=mock_db, flow_id=uuid.uuid4())

    assert deleted is False, "delete_flow must return False when flow not found"
    mock_db.delete.assert_not_awaited()
    mock_db.commit.assert_not_awaited()
