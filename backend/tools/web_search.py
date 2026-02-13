"""Tavily API wrapper for web search."""

import logging
from typing import Any

import httpx

from backend.config import settings

logger = logging.getLogger(__name__)


async def search_web(query: str, max_results: int = 10) -> list[dict[str, Any]]:
    """Search the web using Tavily API."""
    if not settings.TAVILY_API_KEY:
        logger.warning("TAVILY_API_KEY not set, returning empty results")
        return []

    url = "https://api.tavily.com/search"
    payload = {
        "api_key": settings.TAVILY_API_KEY,
        "query": query,
        "search_depth": "basic",
        "max_results": min(max_results, settings.MAX_SEARCH_RESULTS),
        "include_answer": False,
    }

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("results", [])
    except Exception as e:
        logger.warning("Tavily search failed (using Wikipedia/ArXiv only): %s", e)
        return []
