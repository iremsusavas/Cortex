"""ArXiv API for academic paper search."""

import asyncio
import logging
from typing import Any

logger = logging.getLogger(__name__)


def _sync_arxiv_search(query: str, max_results: int) -> list[dict[str, Any]]:
    """Synchronous arxiv search (runs in thread)."""
    import arxiv

    results = []
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance,
    )
    for result in arxiv.Client().results(search):
        results.append(
            {
                "title": result.title,
                "url": result.entry_id,
                "summary": (result.summary or "")[:500],
                "authors": [a.name for a in result.authors],
                "published": result.published.isoformat() if result.published else None,
            }
        )
    return results


async def search_arxiv(query: str, max_results: int = 5) -> list[dict[str, Any]]:
    """Search ArXiv for academic papers."""
    try:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, lambda: _sync_arxiv_search(query, max_results)
        )
    except ImportError:
        logger.warning("arxiv package not installed")
        return []
    except Exception as e:
        logger.exception("ArXiv search failed: %s", e)
        return []
