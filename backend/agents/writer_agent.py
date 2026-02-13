"""Writer agent - generates professional research report."""

import time

from backend.agents.base_agent import BaseAgent
from backend.llm.prompt_templates import WRITER_SYSTEM
from backend.orchestrator.schemas import AgentResult, AgentThought


class WriterAgent(BaseAgent):
    """Generates professional research reports from analysis."""

    def __init__(self, llm_gateway, event_bus):
        super().__init__(
            name="Writer",
            role="Professional research report writer",
            llm_gateway=llm_gateway,
            event_bus=event_bus,
        )

    async def execute(self, task: dict, context: dict) -> AgentResult:
        """Write report from analysis and findings."""
        session_id = context.get("session_id", "")
        analysis = task.get("analysis", {})
        findings = task.get("findings", [])
        plan = task.get("plan", {})
        revision_instructions = task.get("revision_instructions", "")

        start = time.time()

        await self.emit_thought(
            session_id, "thinking", "Writing professional research report..."
        )

        system = WRITER_SYSTEM
        if revision_instructions:
            system += f"\n\nREVISION INSTRUCTIONS:\n{revision_instructions}"

        prompt = f"""Original question: {plan.get('main_topic', '')}

Analysis results:
{analysis}

Findings (sources):
{findings[:15]}

Write a comprehensive research report based on the above information. Use Markdown format. Cite sources in [1], [2] format."""

        result = await self.llm_gateway.complete(
            prompt=prompt,
            system=system,
            temperature=0.3,
        )

        report = result.get("content", "# Report\n\nNo content generated.")

        duration = time.time() - start
        return AgentResult(
            agent_name=self.name,
            success=True,
            output={"report": report},
            thoughts=[],
            total_tokens=result.get("input_tokens", 0) + result.get("output_tokens", 0),
            total_cost=result.get("cost_usd", 0),
            duration_seconds=duration,
        )
