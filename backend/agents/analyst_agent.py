"""Analyst agent - analyzes findings, finds patterns, extracts insights."""

import json
import time

from backend.agents.base_agent import BaseAgent
from backend.llm.prompt_templates import ANALYST_SYSTEM
from backend.orchestrator.schemas import AgentResult, AgentThought


class AnalystAgent(BaseAgent):
    """Analyzes research findings and extracts insights."""

    def __init__(self, llm_gateway, event_bus):
        super().__init__(
            name="Analyst",
            role="Data analyst and pattern recognition expert",
            llm_gateway=llm_gateway,
            event_bus=event_bus,
        )

    async def execute(self, task: dict, context: dict) -> AgentResult:
        """Analyze findings and produce structured analysis."""
        session_id = context.get("session_id", "")
        findings = task.get("findings", [])
        plan = task.get("plan", {})

        start = time.time()

        await self.emit_thought(
            session_id, "thinking", "Analyzing findings and identifying patterns..."
        )

        findings_text = json.dumps(findings[:20], indent=2, ensure_ascii=False)
        prompt = f"""Research findings:
{findings_text}

Original question: {plan.get('main_topic', '')}

Analyze these findings. Identify themes, contradictions, gaps, and key insights. Respond in JSON format."""

        try:
            result, usage = await self.llm_gateway.complete_json(
                prompt=prompt,
                system=ANALYST_SYSTEM,
                temperature=0.3,
            )
            cost_usd = usage.get("cost_usd", 0)
            total_tokens = usage.get("input_tokens", 0) + usage.get("output_tokens", 0)
        except Exception:
            result = {
                "themes": [{"name": "General", "evidence_count": len(findings), "confidence": 0.7}],
                "contradictions": [],
                "gaps": [],
                "key_insights": [{"insight": "Analysis based on gathered sources", "supporting_evidence": [], "confidence": 0.6}],
                "overall_confidence": 0.65,
            }
            cost_usd = 0
            total_tokens = 0

        duration = time.time() - start
        return AgentResult(
            agent_name=self.name,
            success=True,
            output=result,
            thoughts=[],
            total_tokens=total_tokens,
            total_cost=cost_usd,
            duration_seconds=duration,
        )
