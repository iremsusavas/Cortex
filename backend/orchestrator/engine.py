"""Main orchestration engine for research pipeline."""

import asyncio
import logging
import uuid
from datetime import datetime

from backend.agents.planner_agent import PlannerAgent
from backend.agents.researcher_agent import ResearcherAgent
from backend.agents.analyst_agent import AnalystAgent
from backend.agents.writer_agent import WriterAgent
from backend.agents.critic_agent import CriticAgent
from backend.config import settings
from backend.llm.gateway import LLMGateway
from backend.orchestrator.event_bus import event_bus
from backend.orchestrator.state_manager import (
    ResearchPhase,
    ResearchSession,
    Source,
    session_store,
)

logger = logging.getLogger(__name__)


class ResearchOrchestrator:
    """
    Main orchestration engine.

    Flow:
    1. User query -> create ResearchSession
    2. PlannerAgent -> create plan
    3. ResearcherAgent -> parallel research
    4. AnalystAgent -> analyze findings
    5. WriterAgent -> write report
    6. CriticAgent -> quality check
    7. If not approved -> back to Writer (max 2 revisions)
    8. Save final report
    """

    def __init__(self):
        self.llm_gateway = LLMGateway()
        self.planner = PlannerAgent(self.llm_gateway, event_bus)
        self.researcher = ResearcherAgent(self.llm_gateway, event_bus)
        self.analyst = AnalystAgent(self.llm_gateway, event_bus)
        self.writer = WriterAgent(self.llm_gateway, event_bus)
        self.critic = CriticAgent(self.llm_gateway, event_bus)
        self._concurrent_sessions = 0
        self._max_concurrent = settings.MAX_CONCURRENT_RESEARCH

    async def run_research(
        self,
        query: str,
        session_id: str | None = None,
        depth: int = 2,
        language: str = "en",
    ) -> dict:
        """Run full research pipeline."""
        session_id = session_id or str(uuid.uuid4())
        session = ResearchSession(
            id=session_id,
            query=query,
            depth=depth,
            language=language,
        )
        session_store.set(session)

        if self._concurrent_sessions >= self._max_concurrent:
            await event_bus.publish(
                session_id,
                "research.error",
                {"error": "Max concurrent research sessions reached"},
            )
            session.phase = ResearchPhase.FAILED
            session.error = "Rate limited"
            return session.to_dict()

        self._concurrent_sessions += 1
        try:
            # Phase: Planning
            session.phase = ResearchPhase.PLANNING
            await event_bus.publish(
                session_id, "research.phase_change", {"phase": "planning"}
            )

            plan_result = await self.planner.execute(
                {"query": query}, {"session_id": session_id}
            )
            session.plan = plan_result.output
            session.total_tokens += plan_result.total_tokens
            session.total_cost += plan_result.total_cost

            sub_tasks = session.plan.get("sub_tasks", [])[: settings.MAX_SUB_TASKS]
            if not sub_tasks:
                sub_tasks = [{"question": query, "sources": ["web"], "priority": 1}]

            # Phase: Researching
            session.phase = ResearchPhase.RESEARCHING
            await event_bus.publish(
                session_id, "research.phase_change", {"phase": "researching"}
            )

            research_result = await self.researcher.execute(
                {"sub_tasks": sub_tasks}, {"session_id": session_id}
            )
            session.findings = research_result.output.get("findings", [])
            for s in research_result.output.get("sources", []):
                session.sources.append(
                    Source(
                        url=s.get("source_url", ""),
                        title=s.get("source_title"),
                        credibility_score=s.get("credibility_score"),
                        relevance_score=s.get("relevance_score"),
                        content_preview=s.get("finding", "")[:200],
                    )
                )
            session.total_tokens += research_result.total_tokens
            session.total_cost += research_result.total_cost

            # Phase: Analyzing
            session.phase = ResearchPhase.ANALYZING
            await event_bus.publish(
                session_id, "research.phase_change", {"phase": "analyzing"}
            )

            analysis_result = await self.analyst.execute(
                {
                    "findings": session.findings,
                    "plan": session.plan,
                },
                {"session_id": session_id},
            )
            session.analysis = analysis_result.output
            session.total_tokens += analysis_result.total_tokens
            session.total_cost += analysis_result.total_cost

            # Phase: Writing (with possible revisions)
            max_revisions = 2
            for revision in range(max_revisions + 1):
                session.phase = ResearchPhase.REVISING if revision > 0 else ResearchPhase.WRITING
                await event_bus.publish(
                    session_id,
                    "research.phase_change",
                    {"phase": "writing" if revision == 0 else "revising"},
                )

                writer_task = {
                    "analysis": session.analysis,
                    "findings": session.findings,
                    "plan": session.plan,
                }
                if revision > 0 and session.evaluation:
                    writer_task["revision_instructions"] = session.evaluation.get(
                        "revision_instructions", ""
                    )

                writer_result = await self.writer.execute(
                    writer_task, {"session_id": session_id}
                )
                session.report = writer_result.output.get("report", "")
                session.total_tokens += writer_result.total_tokens
                session.total_cost += writer_result.total_cost

                # Phase: Reviewing
                session.phase = ResearchPhase.REVIEWING
                await event_bus.publish(
                    session_id, "research.phase_change", {"phase": "reviewing"}
                )

                critic_result = await self.critic.execute(
                    {
                        "report": session.report,
                        "plan": session.plan,
                        "findings": session.findings,
                    },
                    {"session_id": session_id},
                )
                session.evaluation = critic_result.output
                session.revision_count = revision

                if critic_result.output.get("approved", True):
                    break
                if not critic_result.output.get("revision_needed", False):
                    break

            session.phase = ResearchPhase.COMPLETE
            session.completed_at = datetime.utcnow()
            await event_bus.publish(
                session_id,
                "research.complete",
                {
                    "report": session.report,
                    "evaluation": session.evaluation,
                    "total_cost": session.total_cost,
                },
            )

        except Exception as e:
            logger.exception("Research failed: %s", e)
            session.phase = ResearchPhase.FAILED
            session.error = str(e)
            session.completed_at = datetime.utcnow()
            await event_bus.publish(
                session_id, "research.error", {"error": str(e)}
            )
        finally:
            self._concurrent_sessions -= 1

        return session.to_dict()


orchestrator = ResearchOrchestrator()
