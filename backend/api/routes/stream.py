"""WebSocket stream routes for real-time research updates."""

import asyncio
import json
from datetime import datetime, timezone

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from backend.orchestrator.event_bus import event_bus
from backend.orchestrator.state_manager import session_store

router = APIRouter(tags=["stream"])


async def send_ws_message(websocket: WebSocket, msg: dict) -> None:
    """Send JSON message to WebSocket client."""
    try:
        await websocket.send_json(msg)
    except Exception:
        pass


@router.websocket("/ws/research/{session_id}")
async def websocket_research_stream(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time research updates."""
    await websocket.accept()

    async def event_handler(event: dict) -> None:
        """Forward event to WebSocket client."""
        await send_ws_message(
            websocket,
            {
                "type": event["type"],
                "data": event.get("data", {}),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "session_id": session_id,
            },
        )

    # Subscribe to all events for this session
    event_bus.subscribe(session_id, "*", event_handler)

    try:
        # Send initial state if session exists
        session = session_store.get(session_id)
        if session:
            await send_ws_message(
                websocket,
                {
                    "type": "phase.change",
                    "data": {"phase": session.phase.value},
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "session_id": session_id,
                },
            )

        # Heartbeat loop
        while True:
            await asyncio.sleep(30)
            await send_ws_message(
                websocket,
                {
                    "type": "ping",
                    "data": {},
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "session_id": session_id,
                },
            )
    except WebSocketDisconnect:
        pass
    finally:
        event_bus.unsubscribe(session_id, "*", event_handler)
