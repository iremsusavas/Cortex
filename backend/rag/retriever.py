"""Semantic search retriever with optional reranking."""

from typing import Any

from backend.rag.vector_store import vector_store


class Retriever:
    """Semantic search + optional reranking."""

    async def retrieve(
        self,
        query: str,
        session_id: str,
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        """Retrieve relevant chunks for query."""
        results = await vector_store.search(
            query=query,
            session_id=session_id,
            top_k=top_k,
        )
        return results
