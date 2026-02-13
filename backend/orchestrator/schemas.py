"""Pydantic models for orchestrator events."""

from typing import Any

from pydantic import BaseModel, Field


class AgentThought(BaseModel):
    """Agent thought/activity for UI streaming."""

    agent_name: str
    thought_type: str  # "thinking", "action", "observation", "result", "error"
    content: str
    timestamp: float = Field(default_factory=lambda: __import__("time").time())
    tokens_used: int = 0
    cost_usd: float = 0.0
    metadata: dict = Field(default_factory=dict)


class AgentResult(BaseModel):
    """Result from agent execution."""

    agent_name: str
    success: bool
    output: Any
    thoughts: list[AgentThought] = Field(default_factory=list)
    total_tokens: int = 0
    total_cost: float = 0.0
    duration_seconds: float = 0.0


class SubTask(BaseModel):
    """Research sub-task from planner."""

    id: str
    question: str
    sources: list[str]
    priority: int
    expected_output: str


class ResearchPlan(BaseModel):
    """Full research plan from planner agent."""

    main_topic: str
    complexity_score: int
    sub_tasks: list[SubTask]
    research_strategy: str
    estimated_depth: int


class Finding(BaseModel):
    """Single finding from researcher."""

    finding: str
    source_url: str
    source_title: str
    credibility_score: int
    relevance_score: int
    key_quotes: list[str] = Field(default_factory=list)


class AnalysisResult(BaseModel):
    """Analysis output from analyst agent."""

    themes: list[dict]
    contradictions: list[dict]
    gaps: list[str]
    key_insights: list[dict]
    overall_confidence: float


class CriticResult(BaseModel):
    """Critic evaluation result."""

    overall_score: float
    factual_accuracy: float
    completeness: float
    bias_score: float
    citation_quality: float
    readability: float
    issues: list[dict]
    approved: bool
    revision_needed: bool
    revision_instructions: str
