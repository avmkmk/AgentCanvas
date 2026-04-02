"""
WebSocket connection manager with Redis pub/sub backend (BC-13, M4).

Architecture:
- Each execution gets its own Redis channel: ``execution:{execution_id}``.
- broadcast() publishes to Redis; _redis_listener() subscribes and delivers
  to all locally-connected WebSocket clients.
- In a single-process deployment the message round-trips through Redis
  (negligible latency).  In a multi-process setup it works across instances
  because all processes share the same Redis channel.
- _redis_listener() task is started on first connect for an execution_id and
  cancelled when the last local client disconnects.

Coding Standard 2: Redis connection lazy-initialised in _get_redis() — no
startup-time dependency on Redis being ready at import.
Coding Standard 5: all send and subscribe failures caught; bad connections
removed so they do not block future broadcasts.
Coding Standard 8: Redis client wrapped in service method (_get_redis) —
external dependency never accessed directly from broadcast().
"""
from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

import redis.asyncio as aioredis
from fastapi import WebSocket
from starlette.websockets import WebSocketState

from app.core.config import settings

_log = logging.getLogger(__name__)


class ConnectionManager:
    """Manages active WebSocket connections with Redis pub/sub backend.

    Stateless beyond connection tracking — safe as a module-level singleton.
    """

    def __init__(self) -> None:
        # Maps execution_id string → list of active WebSocket connections
        self._connections: dict[str, list[WebSocket]] = {}
        # Lazy Redis client — initialised on first use
        self._redis: aioredis.Redis | None = None
        # Maps execution_id → asyncio.Task running the Redis subscriber loop
        self._pubsub_tasks: dict[str, asyncio.Task] = {}  # type: ignore[type-arg]

    async def _get_redis(self) -> aioredis.Redis:
        """Return (or create) the shared async Redis client.

        Lazy initialisation avoids a hard startup dependency on Redis.
        decode_responses=True so raw["data"] is already a str.
        """
        if self._redis is None:
            self._redis = aioredis.from_url(
                settings.redis_url, decode_responses=True
            )
        return self._redis

    async def connect(self, websocket: WebSocket, execution_id: str) -> None:
        """Accept and register a WebSocket; start Redis subscriber if needed."""
        await websocket.accept()
        self._connections.setdefault(execution_id, []).append(websocket)

        # Start the Redis subscriber for this execution_id if not already running.
        # One subscriber per execution_id delivers to all local clients.
        if execution_id not in self._pubsub_tasks:
            task = asyncio.create_task(self._redis_listener(execution_id))
            self._pubsub_tasks[execution_id] = task

        _log.debug(
            "WS connected: execution_id=%s total=%d",
            execution_id,
            len(self._connections[execution_id]),
        )

    async def disconnect(self, websocket: WebSocket, execution_id: str) -> None:
        """Remove a WebSocket; cancel Redis listener when no local clients remain."""
        conns = self._connections.get(execution_id, [])
        if websocket in conns:
            conns.remove(websocket)
        if not conns:
            self._connections.pop(execution_id, None)
            # No more local subscribers — cancel the listener task
            task = self._pubsub_tasks.pop(execution_id, None)
            if task is not None:
                task.cancel()
        _log.debug("WS disconnected: execution_id=%s", execution_id)

    async def broadcast(
        self,
        execution_id: str,
        event_type: str,
        payload: dict[str, Any],
    ) -> None:
        """Publish an event to Redis; _redis_listener delivers it to WS clients.

        Publishing to Redis rather than writing to WebSockets directly makes
        this method safe to call from background tasks (FlowExecutor) and from
        request handlers (HITL API) without coupling them to live WS state.
        """
        message: str = json.dumps(
            {
                "event": event_type,
                "execution_id": execution_id,
                "payload": payload,
            }
        )
        try:
            r = await self._get_redis()
            await r.publish(f"execution:{execution_id}", message)
        except Exception as exc:  # noqa: BLE001
            _log.warning(
                "WS broadcast failed to publish to Redis for execution %s: %s",
                execution_id,
                exc,
            )

    async def _redis_listener(self, execution_id: str) -> None:
        """Subscribe to the Redis channel and deliver messages to local clients.

        Runs as a background asyncio.Task per execution_id.
        Exits cleanly when cancelled (disconnect() or process shutdown).
        """
        channel = f"execution:{execution_id}"
        try:
            r = await self._get_redis()
            pubsub = r.pubsub()
            await pubsub.subscribe(channel)
            _log.debug("Redis listener started: channel=%s", channel)

            async for raw in pubsub.listen():
                if raw["type"] != "message":
                    continue
                data: str = raw["data"]
                # Deliver to all local WS connections — copy list first so we
                # can safely mutate _connections during iteration.
                conns = list(self._connections.get(execution_id, []))
                for ws in conns:
                    try:
                        if ws.client_state == WebSocketState.CONNECTED:
                            await ws.send_text(data)
                    except Exception as exc:  # noqa: BLE001
                        _log.warning(
                            "Failed to send WS message to execution %s: %s",
                            execution_id,
                            exc,
                        )
                        await self.disconnect(ws, execution_id)

        except asyncio.CancelledError:
            _log.debug("Redis listener cancelled: channel=%s", channel)
            # Clean up the pubsub subscription before exiting
            try:
                await pubsub.unsubscribe(channel)
                await pubsub.aclose()
            except Exception:  # noqa: BLE001
                pass  # Best-effort cleanup on cancellation
            raise
        except Exception as exc:  # noqa: BLE001
            _log.exception(
                "Redis listener error for execution %s: %s",
                execution_id,
                exc,
            )


# Module-level singleton — shared across all requests in the process
ws_manager = ConnectionManager()
