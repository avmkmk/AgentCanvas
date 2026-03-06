"""
WebSocket connection manager — single-process MVP (BC-08).

Stores per-execution WebSocket connections and broadcasts events.
No Redis pub/sub in M3 — add in M4 for horizontal scaling.

Coding Standard 2: connection list initialised in connect(); cleaned up
in disconnect() and on send failure.
Coding Standard 5: all send failures are caught and logged; the
connection is removed so it does not block future broadcasts.
"""
from __future__ import annotations

import json
import logging
from typing import Any

from fastapi import WebSocket
from starlette.websockets import WebSocketState

_log = logging.getLogger(__name__)


class ConnectionManager:
    """Manages active WebSocket connections keyed by execution_id.

    Thread-safety note: FastAPI runs in a single asyncio event loop per
    process in the M3 MVP. In M4, when horizontal scaling is added, this
    should be replaced with a Redis pub/sub backend.
    """

    def __init__(self) -> None:
        # Maps execution_id string → list of active WebSocket connections
        self._connections: dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, execution_id: str) -> None:
        """Accept and register a new WebSocket connection for *execution_id*."""
        await websocket.accept()
        if execution_id not in self._connections:
            self._connections[execution_id] = []
        self._connections[execution_id].append(websocket)
        _log.debug(
            "WS connected: execution_id=%s total=%d",
            execution_id,
            len(self._connections[execution_id]),
        )

    def disconnect(self, websocket: WebSocket, execution_id: str) -> None:
        """Remove a WebSocket connection from the registry.

        Safe to call even if the connection is not registered — no-op in
        that case (Coding Standard 5 — check before access).
        """
        connections = self._connections.get(execution_id, [])
        if websocket in connections:
            connections.remove(websocket)
        # Prune the key entirely when no connections remain
        if not connections:
            self._connections.pop(execution_id, None)
        _log.debug("WS disconnected: execution_id=%s", execution_id)

    async def broadcast(
        self,
        execution_id: str,
        event_type: str,
        payload: dict[str, Any],
    ) -> None:
        """Send a JSON event to all connections for *execution_id*.

        Connections that fail to receive the message are removed silently
        to avoid blocking subsequent broadcasts (Coding Standard 5).
        """
        message: str = json.dumps(
            {
                "event": event_type,
                "execution_id": execution_id,
                "payload": payload,
            }
        )
        # Iterate over a copy so we can mutate _connections during the loop
        connections = list(self._connections.get(execution_id, []))
        for websocket in connections:
            try:
                if websocket.client_state == WebSocketState.CONNECTED:
                    await websocket.send_text(message)
            except Exception as exc:  # noqa: BLE001
                # Log and discard — do not let one bad connection block others
                _log.warning(
                    "Failed to send WS event '%s' to execution %s: %s",
                    event_type,
                    execution_id,
                    exc,
                )
                self.disconnect(websocket, execution_id)


# Module-level singleton — shared across all requests in the process
ws_manager = ConnectionManager()
