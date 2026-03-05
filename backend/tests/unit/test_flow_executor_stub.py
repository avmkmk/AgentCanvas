"""
Stub tests for FlowExecutor (BC-02).

Two layers of tests:

1. Tests marked PASS: verify the stub's own behaviour — always run.
2. Tests marked xfail: document the real FlowExecutor contract for BC-02.

The stub uses a simple list of agents and produces StepEvent objects.
Tests here validate:
  - Sequential step ordering
  - Early-exit on first failure
  - Event emission order

Coding Standard 1: no recursion — sequential loops only.
Coding Standard 7: both the happy path and failure path are tested.
"""
from __future__ import annotations

import pytest

from tests.stubs.flow_executor_stub import FlowExecutorStub


# ─── Helpers ──────────────────────────────────────────────────────────────────


def _make_agents(n: int) -> list[dict[str, str]]:
    """Return n agent dicts with sequential ids."""
    return [{"id": f"agent-{i}"} for i in range(n)]


# ─── Stub self-tests (always run) ─────────────────────────────────────────────


@pytest.mark.asyncio
async def test_stub_sequential_execution_runs_all_steps() -> None:
    """
    When no step fails, execute() must produce one StepEvent per agent,
    all with status 'completed'.
    """
    agents = _make_agents(3)
    executor = FlowExecutorStub(agents=agents)

    events = await executor.execute()

    assert len(events) == 3, "Must emit one event per agent"
    for i, event in enumerate(events):
        assert event.status == "completed", f"Step {i} must have status 'completed'"
        assert event.step_index == i, f"Step {i} must report index {i}"
        assert event.agent_id == f"agent-{i}"


@pytest.mark.asyncio
async def test_stub_execution_stops_on_first_failure() -> None:
    """
    When fail_at_step=1, execute() must stop after emitting the failed event
    for step 1.  Steps 2, 3, ... must not run.
    """
    agents = _make_agents(4)
    executor = FlowExecutorStub(agents=agents, fail_at_step=1)

    events = await executor.execute()

    # Only steps 0 and 1 should have events; steps 2-3 must be absent
    assert len(events) == 2, (
        "Execution must stop after the first failed step — no subsequent events"
    )
    assert events[0].status == "completed"
    assert events[1].status == "failed"
    assert events[1].step_index == 1


@pytest.mark.asyncio
async def test_stub_step_events_are_emitted_in_order() -> None:
    """
    StepEvent.step_index values must be monotonically increasing.
    This mirrors the requirement that the real FlowExecutor never
    reorders or skips steps.
    """
    agents = _make_agents(5)
    executor = FlowExecutorStub(agents=agents)

    events = await executor.execute()

    for i, event in enumerate(events):
        assert event.step_index == i, (
            f"Event at position {i} must have step_index {i}, got {event.step_index}"
        )


@pytest.mark.asyncio
async def test_stub_first_step_failure_produces_single_event() -> None:
    """
    fail_at_step=0 means the very first agent fails.
    Only one event must be emitted with status 'failed'.
    """
    agents = _make_agents(3)
    executor = FlowExecutorStub(agents=agents, fail_at_step=0)

    events = await executor.execute()

    assert len(events) == 1
    assert events[0].status == "failed"
    assert events[0].step_index == 0


@pytest.mark.asyncio
async def test_stub_empty_agents_produces_no_events() -> None:
    """execute() with no agents must return an empty list, not raise."""
    executor = FlowExecutorStub(agents=[])

    events = await executor.execute()

    assert events == [], "No agents must result in an empty events list"


# ─── Production FlowExecutor contract tests (xfail until BC-02) ───────────────


@pytest.mark.xfail(
    reason="FlowExecutor (BC-02) not implemented — sequential execution contract",
    strict=False,
)
@pytest.mark.asyncio
async def test_sequential_execution_passes_output_to_next_step() -> None:
    """
    The real FlowExecutor must pass each step's output as context to the
    next step's prompt.  The stub does not implement this chaining — this
    test documents the requirement for BC-02.
    """
    agents = _make_agents(2)
    executor = FlowExecutorStub(agents=agents)
    events = await executor.execute()

    # In the real executor, step 1's prompt must include step 0's output
    # The stub returns independent output_{i} strings — this will fail
    assert "output_0" in events[1].output, (
        "Real FlowExecutor must chain step outputs as context"
    )


@pytest.mark.xfail(
    reason="FlowExecutor (BC-02) not implemented — HITL gate pause contract",
    strict=False,
)
@pytest.mark.asyncio
async def test_hitl_gate_pauses_execution() -> None:
    """
    When an agent has a HITL gate configured, the real FlowExecutor must
    pause execution and create a HITLReview before continuing.
    The stub does not model HITL gates — this documents the BC-02 requirement.
    """
    # This test intentionally fails because the stub has no HITL support
    agents = [{"id": "agent-0", "hitl_after": True}]
    executor = FlowExecutorStub(agents=agents)
    events = await executor.execute()

    # Real executor: status should be "paused_hitl" for gated steps
    assert any(e.status == "paused_hitl" for e in events), (
        "Real FlowExecutor must emit a paused_hitl event at HITL gates"
    )
