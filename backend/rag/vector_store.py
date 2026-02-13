"""ChromaDB vector store wrapper."""

import logging
from typing import Any

from backend.config import settings
from backend.rag.embedder import embed

logger = logging.getLogger(__name__)

_chroma_client = None


def _get_client():
    """Lazy load ChromaDB client."""
    global _chroma_client
    if _chroma_client is None:
        try:
            import chromadb
            from chromadb.config import Settings as ChromaSettings

            _chroma_client = chromadb.PersistentClient(
                path=settings.CHROMA_PERSIST_DIR,
                settings=ChromaSettings(anonymized_telemetry=False),
            )
        except Exception as e:
            logger.warning("ChromaDB init failed: %s", e)
            return None
    return _chroma_client


class VectorStore:
    """
    ChromaDB wrapper for research session embeddings.

    Each session gets collection: research_{session_id}
    """

    def __init__(self):
        self.client = _get_client()

    def _collection_name(self, session_id: str) -> str:
        return f"research_{session_id}"

    async def add_documents(
        self,
        texts: list[str],
        metadatas: list[dict],
        session_id: str,
    ) -> None:
        """Add documents to session collection."""
        if not self.client:
            return
        try:
            collection = self.client.get_or_create_collection(
                name=self._collection_name(session_id),
                metadata={"hnsw:space": "cosine"},
            )
            embeddings = embed(texts)
            ids = [f"doc_{i}" for i in range(len(texts))]
            collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
            )
        except Exception as e:
            logger.exception("VectorStore add failed: %s", e)

    async def search(
        self,
        query: str,
        session_id: str,
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        """Semantic search in session collection."""
        if not self.client:
            return []
        try:
            collection = self.client.get_collection(
                name=self._collection_name(session_id)
            )
            query_embedding = embed([query])[0]
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                include=["documents", "metadatas", "distances"],
            )
            return [
                {
                    "text": doc,
                    "metadata": meta or {},
                    "distance": dist,
                }
                for doc, meta, dist in zip(
                    results["documents"][0],
                    results["metadatas"][0],
                    results["distances"][0],
                )
            ]
        except Exception as e:
            logger.exception("VectorStore search failed: %s", e)
            return []

    async def delete_collection(self, session_id: str) -> None:
        """Delete session collection."""
        if not self.client:
            return
        try:
            self.client.delete_collection(name=self._collection_name(session_id))
        except Exception as e:
            logger.warning("Delete collection failed: %s", e)


vector_store = VectorStore()
