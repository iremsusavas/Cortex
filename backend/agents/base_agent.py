"""Abstract base agent class."""

import time
from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator

from backend.orchestrator.schemas import AgentResult, AgentThought


class BaseAgent(ABC):
    """
    Base class for all agents.

    - name: Agent display name (e.g. "Planner", "Researcher")
    - role: Role description for system prompt
    - llm_gateway: LLM abstraction for API calls
    - event_bus: For publishing events to UI
    """

    def __init__(
        self,
        name: str,
        role: str,
        llm_gateway: Any,
        event_bus: Any,
    ):
        self.name = name
        self.role = role
        self.llm_gateway = llm_gateway
        self.event_bus = event_bus

    @abstractmethod
    async def execute(self, task: dict, context: dict) -> AgentResult:
        """Execute agent task. Override in each agent."""
        pass

    async def emit_thought(
        self,
        session_id: str,
        thought_type: str,
        content: str,
        tokens_used: int = 0,
        cost_usd: float = 0.0,
        metadata: dict | None = None,
    ) -> None:
        """Emit thought to event bus for UI streaming."""
        thought = AgentThought(
            agent_name=self.name,
            thought_type=thought_type,
            content=content,
            timestamp=time.time(),
            tokens_used=tokens_used,
            cost_usd=cost_usd,
            metadata=metadata or {},
        )
        await self.event_bus.publish(session_id, "agent.thought", thought.model_dump())
