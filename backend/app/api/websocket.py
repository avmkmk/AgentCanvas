"""
WebSocket endpoint for execution event streaming — BA-12.

Security (S-06, M4): Token-in-query-param auth added.
The browser WebSocket API does not support custom request headers, so
authentication is performed via the ``token`` query parameter instead.
The close code 4001 is in the application-defined range (4000–4999) and
signals to the frontend that reconnection should NOT be retried (auth failure).

Coding Standard 5: WebSocketDisconnect is caught explicitly; the
connection is removed cleanly from the manager.
"""

import hmac

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from app.core.config import settings
from app.core.ws_manager import ws_manager

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/executions/{execution_id}")
async def ws_execution_stream(
    websocket: WebSocket,
    execution_id: str,
    token: str | None = Query(default=None),
) -> None:
    """Stream execution events to the client.

    Authentication: ``?token=<api_key>`` query parameter required.
    Closes with code 4001 if token is absent or incorrect — the frontend
    must NOT retry connections that close with 4001 (permanent auth failure).

    After authentication, keeps the connection alive with a receive loop.
    Any data sent by the client is discarded (server-push only).

    Events pushed by FlowExecutor and HITLManager via ws_manager.broadcast:
    - step_started            {step_number, agent_id, agent_name}
    - step_completed          {step_number, agent_id, agent_name, execution_time_ms}
    - execution_completed     {status, completed_steps, total_steps}
    - execution_failed        {error}
    - hitl_review_pending     {review_id, agent_id, gate_type, output_to_review}
    - hitl_review_decided     {review_id, decision}
    """
    # Validate token before accepting the connection.
    # hmac.compare_digest prevents timing attacks on the key comparison.
    if token is None or not hmac.compare_digest(token, settings.api_key):
        await websocket.close(code=4001)
        return

    await ws_manager.connect(websocket, execution_id)
    try:
        while True:
            # Keep-alive receive loop — detect client disconnect via exception.
            # Discards any incoming data; this is a server-push-only endpoint.
            await websocket.receive_text()
    except WebSocketDisconnect:
        await ws_manager.disconnect(websocket, execution_id)
