"""
WebSocket endpoint for execution event streaming — BA-12.

Coding Standard 5: WebSocketDisconnect is caught explicitly; the
connection is removed cleanly from the manager.

Security note: No API key authentication on the WS endpoint in M3.
The browser WebSocket API does not support custom request headers.
Token-in-query-param auth will be added in M4 (tracked in S-05).
"""
from __future__ import annotations

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.ws_manager import ws_manager

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/executions/{execution_id}")
async def ws_execution_stream(
    websocket: WebSocket,
    execution_id: str,
) -> None:
    """Stream execution events to the client.

    Client connects once and receives push events for the lifetime of the
    execution.  The endpoint keeps the connection alive with a receive loop —
    any data sent by the client is discarded (server-push only in M3).

    Events pushed by FlowExecutor via ws_manager.broadcast:
    - step_started       {step_number, agent_id, agent_name}
    - step_completed     {step_number, agent_id, agent_name, execution_time_ms}
    - execution_completed {status, completed_steps, total_steps}
    - execution_failed   {error}
    """
    await ws_manager.connect(websocket, execution_id)
    try:
        while True:
            # Keep-alive receive loop — detect client disconnect via exception.
            # Discards any incoming data; this is a server-push-only endpoint.
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, execution_id)
