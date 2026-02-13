"""BeautifulSoup web scraper for extracting page content."""

import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)


async def scrape_url(url: str, max_length: int = 10000) -> dict[str, Any]:
    """Scrape a URL and extract main text content."""
    try:
        from bs4 import BeautifulSoup

        async with httpx.AsyncClient(
            timeout=15,
            follow_redirects=True,
            headers={"User-Agent": "Cortex-Research-Bot/1.0"},
        ) as client:
            response = await client.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            # Remove script and style elements
            for tag in soup(["script", "style"]):
                tag.decompose()

            text = soup.get_text(separator=" ", strip=True)
            # Collapse whitespace
            text = " ".join(text.split())[:max_length]

            title = ""
            if soup.title:
                title = soup.title.string or ""

            return {
                "url": url,
                "title": title,
                "content": text,
                "success": True,
            }
    except Exception as e:
        logger.warning("Scrape failed for %s: %s", url, e)
        return {"url": url, "title": "", "content": "", "success": False}
