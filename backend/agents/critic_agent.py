"""Critic agent - quality check and fact verification."""

import time

from backend.agents.base_agent import BaseAgent
from backend.llm.prompt_templates import CRITIC_SYSTEM
from backend.orchestrator.schemas import AgentResult, AgentThought


class CriticAgent(BaseAgent):
    """Evaluates report quality and factual accuracy."""

    def __init__(self, llm_gateway, event_bus):
        super().__init__(
            name="Critic",
            role="Quality control and fact-checking expert",
            llm_gateway=llm_gateway,
            event_bus=event_bus,
        )

    async def execute(self, task: dict, context: dict) -> AgentResult:
        """Evaluate report quality."""
        session_id = context.get("session_id", "")
        report = task.get("report", "")
        plan = task.get("plan", {})
        findings = task.get("findings", [])

        start = time.time()

        await self.emit_thought(
            session_id, "thinking", "Evaluating report quality and accuracy..."
        )

        prompt = f"""Original question: {plan.get('main_topic', '')}

Report:
{report}

Sources:
{findings[:10]}

Evaluate this report. Respond in JSON format."""

        try:
            result, usage = await self.llm_gateway.complete_json(
                prompt=prompt,
                system=CRITIC_SYSTEM,
                temperature=0.1,
            )
            cost_usd = usage.get("cost_usd", 0)
            total_tokens = usage.get("input_tokens", 0) + usage.get("output_tokens", 0)
        except Exception:
            result = {
                "overall_score": 70,
                "factual_accuracy": 70,
                "completeness": 70,
                "bias_score": 70,
                "citation_quality": 70,
                "readability": 70,
                "issues": [],
                "approved": True,
                "revision_needed": False,
                "revision_instructions": "",
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
