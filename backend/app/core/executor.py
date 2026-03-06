"""
FlowExecutor — orchestrates sequential agent execution (BC-02).

Execution lifecycle:
1. start()  — creates FlowExecution record, enqueues background task
2. _run()   — background task entry point; wraps _execute_agents
3. _execute_agents() — loops over agent nodes, calls AgentRunner per step
4. _fail_execution() — marks execution FAILED on unhandled exception
5. cancel() — transitions a running/paused execution to CANCELLED

Coding Standard 1: no recursion — linear loop over agent nodes.
Coding Standard 2: background task uses its own DB session via
_AsyncSessionLocal; never re-uses the request-scoped session.
Coding Standard 5: all exceptions in the background task are caught
and recorded; never silently swallowed.
"""
from __future__ import annotations

import datetime
import logging
import uuid
from typing import Any

from fastapi import BackgroundTasks
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# _AsyncSessionLocal is the async session factory defined in dependencies.py.
# It is used here (not get_db) because background tasks run outside a request
# context and cannot use FastAPI's dependency injection (Coding Standard 2).
from app.api.dependencies import _AsyncSessionLocal  # noqa: PLC2701
from app.core.agent_runner import agent_runner
from app.core.ws_manager import ws_manager
from app.models.flow_execution import ExecutionStatus, FlowExecution
from app.models.step_execution import StepExecution
from app.services.flow_service import FlowService
from app.services.memory_service import memory_service

_log = logging.getLogger(__name__)

_flow_service = FlowService()


class FlowExecutor:
    """Manages the flow execution lifecycle.

    Stateless — safe to use as a module-level singleton.
    """

    async def start(
        self,
        db: AsyncSession,
        flow_id: uuid.UUID,
        background_tasks: BackgroundTasks,
    ) -> FlowExecution:
        """Create a FlowExecution record and schedule the background run.

        Returns the newly created FlowExecution ORM object with status RUNNING.
        Returns None (via FlowService) if the flow does not exist — callers
        should check for a None flow before calling this method.

        Args:
            db: Request-scoped async DB session.
            flow_id: UUID of the flow to execute.
            background_tasks: FastAPI BackgroundTasks for deferred execution.

        Returns:
            Persisted FlowExecution ORM instance.
        """
        flow = await _flow_service.get_flow(db=db, flow_id=flow_id)
        if flow is None:
            from fastapi import HTTPException, status  # local import for layering

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Flow not found",
            )

        # Parse ordered agent node list from the flow canvas config
        flow_config: dict[str, Any] = flow.flow_config or {}
        nodes: list[dict[str, Any]] = flow_config.get("nodes", [])
        # Only count nodes that represent agents (have an agent_id in data)
        agent_nodes: list[dict[str, Any]] = [
            n
            for n in nodes
            if n.get("type") not in ("start", "end")
            and n.get("data", {}).get("agent_id")
        ]
        total_steps: int = len(agent_nodes)

        # Create execution record with status RUNNING (Coding Standard 2)
        execution = FlowExecution(
            id=uuid.uuid4(),
            flow_id=flow_id,
            status=ExecutionStatus.RUNNING.value,
            started_at=datetime.datetime.utcnow(),
            total_steps=total_steps,
            completed_steps=0,
            current_step=0,
        )
        db.add(execution)
        await db.commit()
        await db.refresh(execution)

        # Initialise MongoDB memory for this execution
        await memory_service.init_execution(
            flow_id=flow_id,
            execution_id=execution.id,
        )

        # Schedule background task — uses a new session, not the request session
        background_tasks.add_task(
            self._run,
            str(flow_id),
            str(execution.id),
            agent_nodes,
        )

        _log.info(
            "FlowExecutor.start: execution_id=%s flow_id=%s total_steps=%d",
            execution.id,
            flow_id,
            total_steps,
        )
        return execution

    async def _run(
        self,
        flow_id_str: str,
        execution_id_str: str,
        agent_nodes: list[dict[str, Any]],
    ) -> None:
        """Background task entry point.

        Opens its own DB session (Coding Standard 2 — do not reuse the
        request-scoped session after the HTTP response has been sent).
        """
        flow_id = uuid.UUID(flow_id_str)
        execution_id = uuid.UUID(execution_id_str)

        async with _AsyncSessionLocal() as db:
            try:
                await self._execute_agents(
                    db=db,
                    flow_id=flow_id,
                    execution_id=execution_id,
                    agent_nodes=agent_nodes,
                )
            except Exception as exc:  # noqa: BLE001
                _log.exception(
                    "FlowExecutor: execution %s failed: %s",
                    execution_id_str,
                    exc,
                )
                await self._fail_execution(db, execution_id, str(exc))
                await ws_manager.broadcast(
                    execution_id_str,
                    "execution_failed",
                    {"error": str(exc)},
                )

    async def _execute_agents(
        self,
        db: AsyncSession,
        flow_id: uuid.UUID,
        execution_id: uuid.UUID,
        agent_nodes: list[dict[str, Any]],
    ) -> None:
        """Run each agent node sequentially, updating records after each step.

        Coding Standard 1: flat loop — no recursion, no nested callbacks.
        Delegates per-step work to _execute_single_step for line-count compliance.
        """
        # Local import to avoid circular dependency at module level
        from app.models.agent import Agent

        execution_id_str: str = str(execution_id)

        for step_number, node in enumerate(agent_nodes, start=1):
            agent_id_str: str = node["data"]["agent_id"]
            agent_id = uuid.UUID(agent_id_str)

            agent_result = await db.execute(
                select(Agent).where(Agent.id == agent_id)
            )
            agent = agent_result.scalar_one_or_none()
            if agent is None:
                # Skip missing agents — log and continue (Coding Standard 5)
                _log.warning(
                    "FlowExecutor: agent %s not found — skipping step %d",
                    agent_id_str,
                    step_number,
                )
                continue

            await self._execute_single_step(
                db=db,
                flow_id=flow_id,
                execution_id=execution_id,
                execution_id_str=execution_id_str,
                agent=agent,
                agent_id_str=agent_id_str,
                step_number=step_number,
            )

        await self._complete_execution(db, execution_id, execution_id_str)

    async def _execute_single_step(  # noqa: PLR0913
        self,
        db: AsyncSession,
        flow_id: uuid.UUID,
        execution_id: uuid.UUID,
        execution_id_str: str,
        agent: Any,
        agent_id_str: str,
        step_number: int,
    ) -> None:
        """Run one agent step: update state, call LLM, persist results.

        This method exists purely to keep _execute_agents within 50 lines
        (Coding Standard 6 — one function, one job; max 50 lines).
        """
        # Mark current step on execution record
        exec_result = await db.execute(
            select(FlowExecution).where(FlowExecution.id == execution_id)
        )
        execution = exec_result.scalar_one()
        execution.current_step = step_number
        await db.commit()

        await ws_manager.broadcast(
            execution_id_str,
            "step_started",
            {"step_number": step_number, "agent_id": agent_id_str, "agent_name": agent.name},
        )

        # Create step_execution record
        step_exec = StepExecution(
            id=uuid.uuid4(),
            execution_id=execution_id,
            agent_id=agent.id,
            step_number=step_number,
            status="running",
            started_at=datetime.datetime.utcnow(),
        )
        db.add(step_exec)
        await db.commit()
        await db.refresh(step_exec)

        shared_memory: dict[str, Any] = await memory_service.get_shared_memory(flow_id)
        started_at = datetime.datetime.utcnow()
        output: dict[str, Any] = await agent_runner.run(
            agent=agent,
            shared_memory=shared_memory,
            execution_id=execution_id_str,
            step_number=step_number,
        )
        completed_at = datetime.datetime.utcnow()
        elapsed_ms: int = int((completed_at - started_at).total_seconds() * 1000)

        # Persist step output and update shared memory
        step_exec.status = "completed"
        step_exec.output_data = {"output": output.get("output", "")}
        step_exec.completed_at = completed_at
        step_exec.execution_time_ms = elapsed_ms
        await db.commit()

        await memory_service.update_shared_memory(
            flow_id, {agent.name: output.get("output", "")}
        )

        # Update execution completed_steps counter
        exec_result2 = await db.execute(
            select(FlowExecution).where(FlowExecution.id == execution_id)
        )
        execution = exec_result2.scalar_one()
        execution.completed_steps = step_number
        await db.commit()

        await ws_manager.broadcast(
            execution_id_str,
            "step_completed",
            {
                "step_number": step_number,
                "agent_id": agent_id_str,
                "agent_name": agent.name,
                "execution_time_ms": elapsed_ms,
            },
        )

    async def _complete_execution(
        self,
        db: AsyncSession,
        execution_id: uuid.UUID,
        execution_id_str: str,
    ) -> None:
        """Mark the FlowExecution as COMPLETED and broadcast the final event."""
        final_result = await db.execute(
            select(FlowExecution).where(FlowExecution.id == execution_id)
        )
        final_execution = final_result.scalar_one()
        final_execution.status = ExecutionStatus.COMPLETED.value
        final_execution.completed_at = datetime.datetime.utcnow()
        total: int = final_execution.total_steps
        # success_rate: completed_steps / total_steps (1.0 if flow has no steps)
        final_execution.success_rate = (
            final_execution.completed_steps / total if total > 0 else 1.0
        )
        await db.commit()

        await ws_manager.broadcast(
            execution_id_str,
            "execution_completed",
            {
                "status": "completed",
                "completed_steps": final_execution.completed_steps,
                "total_steps": total,
            },
        )
        _log.info(
            "FlowExecutor: execution %s completed — %d/%d steps",
            execution_id_str,
            final_execution.completed_steps,
            total,
        )

    async def _fail_execution(
        self,
        db: AsyncSession,
        execution_id: uuid.UUID,
        error_message: str,
    ) -> None:
        """Mark a FlowExecution as FAILED with the given error message."""
        result = await db.execute(
            select(FlowExecution).where(FlowExecution.id == execution_id)
        )
        execution = result.scalar_one_or_none()
        if execution is not None:
            execution.status = ExecutionStatus.FAILED.value
            execution.error_message = error_message
            execution.completed_at = datetime.datetime.utcnow()
            await db.commit()

    async def cancel(
        self,
        db: AsyncSession,
        execution_id: uuid.UUID,
    ) -> FlowExecution | None:
        """Cancel a running or paused execution.

        Returns the updated FlowExecution, or None if not found.
        Only RUNNING and PAUSED_HITL executions can be cancelled — other
        statuses are ignored (idempotent for terminal states).
        """
        result = await db.execute(
            select(FlowExecution).where(FlowExecution.id == execution_id)
        )
        execution = result.scalar_one_or_none()
        if execution is None:
            return None

        # Only cancel if in a cancellable state
        cancellable_statuses: frozenset[str] = frozenset(
            {ExecutionStatus.RUNNING.value, ExecutionStatus.PAUSED_HITL.value}
        )
        if execution.status in cancellable_statuses:
            execution.status = ExecutionStatus.CANCELLED.value
            execution.completed_at = datetime.datetime.utcnow()
            await db.commit()
            await db.refresh(execution)

        return execution


# Module-level singleton (Coding Standard 4)
flow_executor = FlowExecutor()
