"""Researcher agent - web search, RAG retrieval, source gathering."""

import asyncio
import time

from backend.agents.base_agent import BaseAgent
from backend.config import settings
from backend.llm.prompt_templates import RESEARCHER_SYSTEM
from backend.orchestrator.schemas import AgentResult, AgentThought
from backend.tools.web_search import search_web
from backend.tools.wikipedia import search_wikipedia
from backend.tools.arxiv import search_arxiv
from backend.tools.scraper import scrape_url


class ResearcherAgent(BaseAgent):
    """Gathers information from web, Wikipedia, and ArXiv."""

    def __init__(self, llm_gateway, event_bus):
        super().__init__(
            name="Researcher",
            role="Research assistant",
            llm_gateway=llm_gateway,
            event_bus=event_bus,
        )

    async def execute(self, task: dict, context: dict) -> AgentResult:
        """Execute research for sub-tasks."""
        session_id = context.get("session_id", "")
        sub_tasks = task.get("sub_tasks", [])[: settings.MAX_SUB_TASKS]
        findings: list[dict] = []
        all_sources: list[dict] = []
        skip_scraping = settings.SKIP_SCRAPING
        max_per_source = settings.MAX_SOURCES_PER_TASK

        start = time.time()
        total_tokens = 0
        total_cost = 0.0

        for st in sorted(sub_tasks, key=lambda x: x.get("priority", 5)):
            question = st.get("question", "")
            sources = st.get("sources", ["web"])

            await self.emit_thought(
                session_id, "action", f"Searching for: {question[:80]}..."
            )

            # Parallel search
            tasks_to_run = []
            if "web" in sources:
                tasks_to_run.append(("web", search_web(question)))
            if "wikipedia" in sources:
                tasks_to_run.append(("wikipedia", search_wikipedia(question)))
            if "arxiv" in sources:
                tasks_to_run.append(("arxiv", search_arxiv(question)))

            results = await asyncio.gather(
                *[t[1] for t in tasks_to_run], return_exceptions=True
            )

            for (source_type, _), result in zip(tasks_to_run, results):
                if isinstance(result, Exception):
                    continue
                for item in result[:max_per_source]:
                    url = item.get("url", "")
                    title = item.get("title", item.get("title", ""))
                    content = item.get("content", item.get("summary", item.get("snippet", "")))

                    if url and not content and source_type == "web" and not skip_scraping:
                        scraped = await scrape_url(url)
                        content = scraped.get("content", "")
                        if scraped.get("title"):
                            title = scraped["title"]

                    credibility = 7 if "wikipedia" in source_type or "arxiv" in source_type else 6
                    finding = {
                        "finding": content[:500] if content else title,
                        "source_url": url,
                        "source_title": title or url,
                        "credibility_score": credibility,
                        "relevance_score": 8,
                        "key_quotes": [],
                    }
                    findings.append(finding)
                    all_sources.append(finding)
                    await self.event_bus.publish(
                        session_id, "source.found", {"source": finding}
                    )

        duration = time.time() - start
        return AgentResult(
            agent_name=self.name,
            success=True,
            output={"findings": findings, "sources": all_sources},
            thoughts=[],
            total_tokens=total_tokens,
            total_cost=total_cost,
            duration_seconds=duration,
        )
