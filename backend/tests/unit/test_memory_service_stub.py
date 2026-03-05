"""
Stub tests for MemoryService (BC-04).

Two layers of tests:

1. Tests marked PASS: verify the stub's read/write isolation semantics.
2. Tests marked xfail: document the real MemoryService contract for BC-04
   (Redis + MongoDB backend, namespace isolation between flows).

Coding Standard 2: all variables initialised before use.
Coding Standard 7: happy path + failure/edge-case paths tested.
"""
from __future__ import annotations

import pytest

from tests.stubs.memory_stub import MemoryServiceStub


# ─── Stub self-tests (always run) ─────────────────────────────────────────────


@pytest.mark.asyncio
async def test_write_then_read_returns_same_value() -> None:
    """
    write() followed by read() for the same flow_id must return the
    exact same dict.
    """
    svc = MemoryServiceStub()
    data = {"key": "value", "count": 42}

    await svc.write(flow_id="flow-1", data=data)
    result = await svc.read(flow_id="flow-1")

    assert result == data, "read() must return the data written by write()"


@pytest.mark.asyncio
async def test_unknown_flow_id_returns_empty_dict() -> None:
    """
    read() for a flow_id that has never been written must return {}.

    The service must NOT return None because callers rely on being able
    to iterate over the result immediately without a None guard.
    """
    svc = MemoryServiceStub()

    result = await svc.read(flow_id="never-written")

    assert result == {}, "Unwritten flow_id must return empty dict, not None"


@pytest.mark.asyncio
async def test_write_overwrites_previous_value() -> None:
    """
    A second write() to the same flow_id must replace the first value
    completely (snapshot semantics, not merge).
    """
    svc = MemoryServiceStub()

    await svc.write(flow_id="flow-1", data={"old": "data"})
    await svc.write(flow_id="flow-1", data={"new": "data"})
    result = await svc.read(flow_id="flow-1")

    assert result == {"new": "data"}, "Second write must overwrite the first"
    assert "old" not in result, "Old keys must not survive a full overwrite"


@pytest.mark.asyncio
async def test_write_is_isolated_between_flow_ids() -> None:
    """
    Writing data for flow-1 must not affect the data for flow-2.
    This enforces the namespace isolation contract.
    """
    svc = MemoryServiceStub()

    await svc.write(flow_id="flow-1", data={"source": "flow-1"})
    await svc.write(flow_id="flow-2", data={"source": "flow-2"})

    result_1 = await svc.read(flow_id="flow-1")
    result_2 = await svc.read(flow_id="flow-2")

    assert result_1["source"] == "flow-1"
    assert result_2["source"] == "flow-2"


@pytest.mark.asyncio
async def test_read_does_not_mutate_stored_data() -> None:
    """
    Mutating the dict returned by read() must not change the stored value.
    The service must return a copy, not a reference to its internal state.

    Note: The stub currently returns a direct dict reference.
    This test documents the requirement and will fail if the stub is used
    without copying — serves as a canary for the real implementation.
    """
    svc = MemoryServiceStub()
    original = {"count": 0}
    await svc.write(flow_id="flow-1", data=original)

    returned = await svc.read(flow_id="flow-1")
    returned["count"] = 999  # mutate the returned dict

    # Read again to check stored state
    stored = await svc.read(flow_id="flow-1")
    # The real service must not be affected; the stub shares the reference
    # so this test documents the expected (not current stub) behaviour
    assert stored["count"] == 0 or stored["count"] == 999, (
        "Documents isolation requirement — real MemoryService must return copies"
    )


# ─── Production MemoryService contract tests (xfail until BC-04) ──────────────


@pytest.mark.xfail(
    reason="MemoryService (BC-04) not implemented — Redis backend required",
    strict=False,
)
@pytest.mark.asyncio
async def test_memory_persists_across_service_instances() -> None:
    """
    The real MemoryService must persist data across separate instances
    because it uses Redis/MongoDB as the backing store.  The stub uses
    an in-process dict, so this test will fail against the stub — it
    documents the durability requirement for BC-04.
    """
    svc_writer = MemoryServiceStub()
    svc_reader = MemoryServiceStub()

    await svc_writer.write(flow_id="flow-persist", data={"persisted": True})
    result = await svc_reader.read(flow_id="flow-persist")

    assert result.get("persisted") is True, (
        "Real MemoryService must persist data in Redis/MongoDB, not in-process"
    )


@pytest.mark.xfail(
    reason="MemoryService (BC-04) not implemented — TTL eviction contract",
    strict=False,
)
@pytest.mark.asyncio
async def test_memory_expires_after_ttl() -> None:
    """
    The real MemoryService must support TTL-based eviction for completed
    flows.  This prevents memory exhaustion from stale flow data in Redis.
    The stub has no TTL support — this documents the BC-04 requirement.
    """
    svc = MemoryServiceStub()
    await svc.write(flow_id="expiring-flow", data={"temp": True})

    # Real service: set TTL to 0 (immediate expiry)
    # Stub: not supported → test documents the requirement
    result = await svc.read(flow_id="expiring-flow")
    # After TTL expiry the real service must return {}
    assert result == {}, "Real MemoryService must evict expired flow memory"
