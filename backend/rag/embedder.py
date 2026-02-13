"""Text embedding using sentence-transformers."""

import logging
from typing import Any

from backend.config import settings

logger = logging.getLogger(__name__)

_embedder = None


def get_embedder():
    """Lazy load embedder model."""
    global _embedder
    if _embedder is None:
        try:
            from sentence_transformers import SentenceTransformer  # type: ignore

            _embedder = SentenceTransformer(settings.EMBEDDING_MODEL)
        except ImportError:
            logger.warning("sentence-transformers not installed")
            return None
    return _embedder


def embed(texts: list[str]) -> list[list[float]]:
    """Embed list of texts. Returns list of vectors."""
    model = get_embedder()
    if model is None:
        return [[0.0] * 384 for _ in texts]  # Fallback dummy vectors
    return model.encode(texts, convert_to_numpy=True).tolist()
