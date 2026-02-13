"""Planner agent - decomposes query into sub-tasks."""

import json
import time

from backend.agents.base_agent import BaseAgent
from backend.llm.prompt_templates import PLANNER_SYSTEM
from backend.orchestrator.schemas import AgentResult, AgentThought, ResearchPlan, SubTask


class PlannerAgent(BaseAgent):
    """Decomposes user query into researchable sub-tasks."""

    def __init__(self, llm_gateway, event_bus):
        super().__init__(
            name="Planner",
            role="Research planning expert",
            llm_gateway=llm_gateway,
            event_bus=event_bus,
        )

    async def execute(self, task: dict, context: dict) -> AgentResult:
        """Create research plan from user query."""
        session_id = context.get("session_id", "")
        query = task.get("query", "")

        thoughts: list[AgentThought] = []
        start = time.time()

        await self.emit_thought(
            session_id, "thinking", "Analyzing query and creating research plan..."
        )

        prompt = f"""User question: {query}

Analyze this question and create a research plan. Respond in JSON format."""

        result, usage = await self.llm_gateway.complete_json(
            prompt=prompt,
            system=PLANNER_SYSTEM,
            temperature=0.3,
        )

        # Validate and parse
        try:
            plan = ResearchPlan(**result)
        except Exception:
            # Fallback minimal plan
            plan = ResearchPlan(
                main_topic=query[:100],
                complexity_score=5,
                sub_tasks=[
                    SubTask(
                        id="task_1",
                        question=query,
                        sources=["web", "wikipedia"],
                        priority=1,
                        expected_output="Comprehensive answer",
                    )
                ],
                research_strategy="Web and Wikipedia search",
                estimated_depth=2,
            )

        for st in plan.sub_tasks:
            await self.event_bus.publish(
                session_id, "plan_created", {"sub_task": st.model_dump()}
            )

        duration = time.time() - start
        return AgentResult(
            agent_name=self.name,
            success=True,
            output=plan.model_dump(),
            thoughts=thoughts,
            total_tokens=usage.get("input_tokens", 0) + usage.get("output_tokens", 0),
            total_cost=usage.get("cost_usd", 0),
            duration_seconds=duration,
        )
