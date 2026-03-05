"""
Stub for FlowExecutor (BC-02).

Models the expected execute() interface used by test_flow_executor_stub.py
and future unit tests for the real FlowExecutor once BC-02 is implemented.

Coding Standard 1: simple linear control flow — no recursion.
Coding Standard 3: explicit dataclass fields, no magic dict keys.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class StepEvent:
    """Represents one agent execution step inside a flow."""

    step_index: int
    agent_id: str
    status: str  # "running" | "completed" | "failed"
    output: str = ""


class FlowExecutorStub:
    """
    Minimal stub matching the expected FlowExecutor interface.

    Parameters
    ----------
    agents:
        List of dicts with at least {"id": str} keys.
    fail_at_step:
        Index of the step that should produce a "failed" StepEvent.
        -1 means no step fails (all complete successfully).
    """

    def __init__(
        self, agents: list[dict[str, str]], fail_at_step: int = -1
    ) -> None:
        self._agents = agents
        self._fail_at_step = fail_at_step
        self.events: list[StepEvent] = []

    async def execute(self) -> list[StepEvent]:
        """
        Execute agents sequentially.

        Stops at the first failing step — mirrors real FlowExecutor
        behaviour where a failed step must not cascade to subsequent agents.
        """
        for i, agent in enumerate(self._agents):
            if i == self._fail_at_step:
                event = StepEvent(
                    step_index=i,
                    agent_id=agent["id"],
                    status="failed",
                )
                self.events.append(event)
                # Stop — do not run subsequent steps after a failure
                break
            event = StepEvent(
                step_index=i,
                agent_id=agent["id"],
                status="completed",
                output=f"output_{i}",
            )
            self.events.append(event)
        return self.events
