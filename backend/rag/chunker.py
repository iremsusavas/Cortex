"""Semantic-aware text chunking."""

import re
from typing import Any

from backend.config import settings


class IntelligentChunker:
    """
    Semantic-aware text chunking.

    Strategy:
    1. Split by paragraphs first
    2. Check sentence boundaries
    3. Split at CHUNK_SIZE (512 tokens), respect sentence boundaries
    4. Add CHUNK_OVERLAP (50 tokens) overlap
    5. Add metadata to each chunk
    """

    def __init__(
        self,
        chunk_size: int | None = None,
        chunk_overlap: int | None = None,
    ):
        self.chunk_size = chunk_size or settings.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP

    def _estimate_tokens(self, text: str) -> int:
        """Rough token estimate (~4 chars per token)."""
        return len(text) // 4

    def _split_sentences(self, text: str) -> list[str]:
        """Split text into sentences."""
        # Simple sentence split on . ! ?
        parts = re.split(r'(?<=[.!?])\s+', text)
        return [p.strip() for p in parts if p.strip()]

    def chunk(
        self,
        text: str,
        metadata: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Chunk text with overlap and metadata.

        Returns list of {"text": str, "metadata": dict}.
        """
        metadata = metadata or {}
        chunks = []
        paragraphs = text.split("\n\n")
        current_chunk = []
        current_tokens = 0

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            sentences = self._split_sentences(para)
            for sent in sentences:
                sent_tokens = self._estimate_tokens(sent)
                if current_tokens + sent_tokens > self.chunk_size and current_chunk:
                    chunk_text = " ".join(current_chunk)
                    chunks.append(
                        {
                            "text": chunk_text,
                            "metadata": {
                                **metadata,
                                "chunk_index": len(chunks),
                            },
                        }
                    )
                    # Overlap: keep last N tokens
                    overlap_tokens = 0
                    overlap_sents = []
                    for s in reversed(current_chunk):
                        overlap_sents.insert(0, s)
                        overlap_tokens += self._estimate_tokens(s)
                        if overlap_tokens >= self.chunk_overlap:
                            break
                    current_chunk = overlap_sents
                    current_tokens = sum(
                        self._estimate_tokens(s) for s in current_chunk
                    )
                current_chunk.append(sent)
                current_tokens += sent_tokens

        if current_chunk:
            chunk_text = " ".join(current_chunk)
            chunks.append(
                {
                    "text": chunk_text,
                    "metadata": {
                        **metadata,
                        "chunk_index": len(chunks),
                        "total_chunks": len(chunks) + 1,
                    },
                }
            )

        # Update total_chunks in all
        for c in chunks:
            c["metadata"]["total_chunks"] = len(chunks)

        return chunks
