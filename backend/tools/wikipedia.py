"""Wikipedia API wrapper."""

import logging
from typing import Any

logger = logging.getLogger(__name__)


async def search_wikipedia(query: str, max_results: int = 3) -> list[dict[str, Any]]:
    """Search Wikipedia and return summaries."""
    try:
        import wikipedia

        wikipedia.set_lang("en")
        results = []
        try:
            search_results = wikipedia.search(query, results=max_results)
            for title in search_results:
                try:
                    page = wikipedia.page(title, auto_suggest=False)
                    results.append(
                        {
                            "title": page.title,
                            "url": page.url,
                            "summary": page.summary[:500] if page.summary else "",
                            "content": page.content[:2000] if page.content else "",
                        }
                    )
                except wikipedia.exceptions.DisambiguationError:
                    continue
                except wikipedia.exceptions.PageError:
                    continue
        except wikipedia.exceptions.WikipediaException:
            pass
        return results
    except ImportError:
        logger.warning("wikipedia package not installed")
        return []
    except Exception as e:
        logger.exception("Wikipedia search failed: %s", e)
        return []
