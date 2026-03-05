"""
MemoryService — MongoDB-backed shared and per-agent memory.

BC-04: execution-scoped shared memory (init, get, update, append log)
BC-05: per-agent memory (get, update)

Coding Standard 2: client created once; connections managed by motor's
internal pool — no manual open/close required.
Coding Standard 8: all inputs validated by callers (Pydantic); this
service trusts that uuid.UUID objects and dict values are correct types.
"""
from __future__ import annotations

import datetime
import logging
import uuid
from typing import Any

from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings

logger = logging.getLogger(__name__)


class MemoryService:
    """MongoDB-backed memory service.

    Two collections are used:
    - ``flow_memory``    — per-flow shared + agent memories (upserted on first access)
    - ``execution_logs`` — append-only execution log entries
    """

    def __init__(self) -> None:
        # Motor creates a connection pool internally; one client per process
        # is the recommended pattern (Coding Standard 2 — resource management).
        self._client: AsyncIOMotorClient = AsyncIOMotorClient(  # type: ignore[var-annotated]
            settings.mongo_uri
        )
        self._db = self._client.orchestrator

    # ------------------------------------------------------------------
    # BC-04 — execution-scoped shared memory
    # ------------------------------------------------------------------

    async def init_execution(
        self,
        flow_id: uuid.UUID,
        execution_id: uuid.UUID,
    ) -> None:
        """Create the initial memory document for a new execution.

        Uses $setOnInsert so subsequent calls are idempotent — the document
        is only created if it does not already exist for this flow_id.
        """
        await self._db.flow_memory.update_one(
            {"flow_id": str(flow_id)},
            {
                "$setOnInsert": {
                    "flow_id": str(flow_id),
                    "shared_memory": {},
                    "agent_memories": {},
                    "execution_logs": [],
                }
            },
            upsert=True,
        )
        logger.debug(
            "MemoryService.init_execution: flow_id=%s execution_id=%s",
            flow_id,
            execution_id,
        )

    async def get_shared_memory(self, flow_id: uuid.UUID) -> dict[str, Any]:
        """Return the shared memory dict for a flow.

        Returns an empty dict if no document exists for this flow_id.
        """
        doc = await self._db.flow_memory.find_one({"flow_id": str(flow_id)})
        if doc is None:
            return {}
        return dict(doc.get("shared_memory", {}))

    async def update_shared_memory(
        self,
        flow_id: uuid.UUID,
        updates: dict[str, Any],
    ) -> None:
        """Merge *updates* into the shared memory dict for a flow.

        Uses dot-notation field paths so existing keys are not overwritten
        unless explicitly included in *updates*.
        """
        # Build $set fields with dot-notation paths (Coding Standard 3)
        set_fields: dict[str, Any] = {
            f"shared_memory.{k}": v for k, v in updates.items()
        }
        await self._db.flow_memory.update_one(
            {"flow_id": str(flow_id)},
            {"$set": set_fields},
            upsert=True,
        )

    async def append_execution_log(
        self,
        execution_id: uuid.UUID,
        entry: dict[str, Any],
    ) -> None:
        """Append a structured log entry to the execution_logs collection.

        Each entry is timestamped here so callers do not need to provide it.
        """
        log_entry: dict[str, Any] = {
            "execution_id": str(execution_id),
            "timestamp": datetime.datetime.utcnow().isoformat(),
            **entry,
        }
        await self._db.execution_logs.update_one(
            {"execution_id": str(execution_id)},
            {"$push": {"logs": log_entry}},
            upsert=True,
        )

    # ------------------------------------------------------------------
    # BC-05 — per-agent memory
    # ------------------------------------------------------------------

    async def get_agent_memory(
        self,
        flow_id: uuid.UUID,
        agent_id: uuid.UUID,
    ) -> dict[str, Any]:
        """Return memory for a specific agent within a flow.

        Returns an empty dict if the document or agent key does not exist.
        """
        doc = await self._db.flow_memory.find_one({"flow_id": str(flow_id)})
        if doc is None:
            return {}
        agent_memories: dict[str, Any] = doc.get("agent_memories", {})
        return dict(agent_memories.get(str(agent_id), {}))

    async def update_agent_memory(
        self,
        flow_id: uuid.UUID,
        agent_id: uuid.UUID,
        data: dict[str, Any],
    ) -> None:
        """Upsert agent-specific memory within the flow's memory document.

        Keys are stored under ``agent_memories.<agent_id>.<key>`` so
        different agents' memories are isolated within the same document.
        """
        set_fields: dict[str, Any] = {
            f"agent_memories.{agent_id!s}.{k}": v for k, v in data.items()
        }
        await self._db.flow_memory.update_one(
            {"flow_id": str(flow_id)},
            {"$set": set_fields},
            upsert=True,
        )


# Module-level singleton (Coding Standard 4 — one way to access the service)
memory_service = MemoryService()
