"""Research session state machine."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from backend.orchestrator.schemas import AgentThought


class ResearchPhase(str, Enum):
    """Research session phases."""

    QUEUED = "queued"
    PLANNING = "planning"
    RESEARCHING = "researching"
    ANALYZING = "analyzing"
    WRITING = "writing"
    REVIEWING = "reviewing"
    REVISING = "revising"
    COMPLETE = "complete"
    FAILED = "failed"


@dataclass
class Source:
    """Source document."""

    url: str
    title: str | None = None
    credibility_score: float | None = None
    relevance_score: float | None = None
    content_preview: str | None = None


@dataclass
class ResearchSession:
    """
    In-memory research session state.

    Persisted to DB at key points.
    """

    id: str
    query: str
    phase: ResearchPhase = ResearchPhase.QUEUED
    plan: dict | None = None
    findings: list[dict] = field(default_factory=list)
    analysis: dict | None = None
    report: str | None = None
    evaluation: dict | None = None
    sources: list[Source] = field(default_factory=list)
    agent_thoughts: list[AgentThought] = field(default_factory=list)
    total_tokens: int = 0
    total_cost: float = 0.0
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None
    revision_count: int = 0
    depth: int = 2
    language: str = "en"
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dict for API/WebSocket."""
        return {
            "id": self.id,
            "query": self.query,
            "phase": self.phase.value,
            "plan": self.plan,
            "findings": self.findings,
            "analysis": self.analysis,
            "report": self.report,
            "evaluation": self.evaluation,
            "sources": [
                {
                    "url": s.url,
                    "title": s.title,
                    "credibility_score": s.credibility_score,
                    "relevance_score": s.relevance_score,
                }
                for s in self.sources
            ],
            "total_tokens": self.total_tokens,
            "total_cost": self.total_cost,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "revision_count": self.revision_count,
            "error": self.error,
        }


class SessionStore:
    """In-memory store for active research sessions."""

    def __init__(self):
        self._sessions: dict[str, ResearchSession] = {}

    def get(self, session_id: str) -> ResearchSession | None:
        return self._sessions.get(session_id)

    def set(self, session: ResearchSession) -> None:
        self._sessions[session.id] = session

    def delete(self, session_id: str) -> None:
        if session_id in self._sessions:
            del self._sessions[session_id]

    def list_all(self, limit: int = 20, offset: int = 0) -> list[ResearchSession]:
        sessions = list(self._sessions.values())
        return sessions[offset : offset + limit]


session_store = SessionStore()
