"""Async publish/subscribe event system for real-time updates."""

import asyncio
import logging
from collections import defaultdict
from typing import Any, Callable, Coroutine

logger = logging.getLogger(__name__)

# Event types
EVENT_AGENT_THOUGHT = "agent.thought"
EVENT_AGENT_ACTION = "agent.action"
EVENT_AGENT_RESULT = "agent.result"
EVENT_PHASE_CHANGE = "research.phase_change"
EVENT_PROGRESS = "research.progress"
EVENT_COMPLETE = "research.complete"
EVENT_ERROR = "research.error"
EVENT_SOURCE_FOUND = "source.found"
EVENT_PLAN_CREATED = "plan_created"


class EventBus:
    """
    Async publish/subscribe event system.

    Each session has its own event bus. Subscribers receive events
    for their session only.
    """

    def __init__(self):
        self._subscribers: dict[str, dict[str, list[Callable]]] = defaultdict(
            lambda: defaultdict(list)
        )
        self._event_buffer: dict[str, list[dict]] = defaultdict(list)
        self._lock = asyncio.Lock()

    def subscribe(
        self, session_id: str, event_type: str, callback: Callable[..., Coroutine]
    ) -> None:
        """Subscribe to events for a session."""
        self._subscribers[session_id][event_type].append(callback)

    def unsubscribe(
        self, session_id: str, event_type: str, callback: Callable[..., Coroutine]
    ) -> None:
        """Unsubscribe from events."""
        if session_id in self._subscribers and event_type in self._subscribers[session_id]:
            try:
                self._subscribers[session_id][event_type].remove(callback)
            except ValueError:
                pass

    async def publish(self, session_id: str, event_type: str, data: dict) -> None:
        """Publish event to all subscribers of this session."""
        event = {"type": event_type, "data": data, "session_id": session_id}
        async with self._lock:
            self._event_buffer[session_id].append(event)

        callbacks = self._subscribers[session_id].get(event_type, [])
        callbacks_all = self._subscribers[session_id].get("*", [])

        for cb in callbacks + callbacks_all:
            try:
                await cb(event)
            except Exception as e:
                logger.exception("Event callback error: %s", e)

    def get_buffered_events(self, session_id: str, since_index: int = 0) -> list[dict]:
        """Get buffered events for reconnection (missed events)."""
        events = self._event_buffer.get(session_id, [])
        return events[since_index:]

    def clear_buffer(self, session_id: str) -> None:
        """Clear event buffer for session (after complete)."""
        if session_id in self._event_buffer:
            del self._event_buffer[session_id]


# Global event bus instance
event_bus = EventBus()
