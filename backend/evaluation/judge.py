"""LLM-as-a-judge evaluator for report quality."""

import logging
from typing import Any

from backend.llm.gateway import LLMGateway

logger = logging.getLogger(__name__)

EVAL_SYSTEM = """You are an expert evaluator for research reports. Evaluate the report on these criteria (0-100 each):
1. Factual Accuracy: Are claims consistent with sources?
2. Completeness: Does it fully answer the original question?
3. Coherence: Is the report logically consistent?
4. Citation Quality: Are claims properly sourced?
5. Objectivity: Is the report balanced?
6. Readability: Is it clear and well-structured?

Respond with valid JSON only:
{
  "factual_accuracy": float,
  "completeness": float,
  "coherence": float,
  "citation_quality": float,
  "objectivity": float,
  "readability": float,
  "overall_score": float,
  "summary": "string"
}

Weights: accuracy=0.25, completeness=0.20, coherence=0.15, citations=0.20, objectivity=0.10, readability=0.10
overall_score = weighted average of the 6 scores."""

WEIGHTS = {
    "factual_accuracy": 0.25,
    "completeness": 0.20,
    "coherence": 0.15,
    "citation_quality": 0.20,
    "objectivity": 0.10,
    "readability": 0.10,
}


class LLMJudge:
    """LLM-as-a-judge for report evaluation."""

    def __init__(self):
        self.llm = LLMGateway()

    async def evaluate(
        self,
        report: str,
        query: str,
        sources: list[dict] | None = None,
    ) -> dict[str, Any]:
        """Evaluate report quality."""
        sources_text = ""
        if sources:
            sources_text = "\n".join(
                f"- {s.get('title', s.get('url', ''))}: {str(s.get('content_preview', ''))[:200]}"
                for s in sources[:10]
            )
        prompt = f"""Original question: {query}

Sources used:
{sources_text or 'N/A'}

Report to evaluate:
{report[:8000]}

Evaluate and return JSON."""

        try:
            result, _ = await self.llm.complete_json(
                prompt=prompt,
                system=EVAL_SYSTEM,
                temperature=0.1,
            )
            return result
        except Exception as e:
            logger.exception("Evaluation failed: %s", e)
            return {
                "overall_score": 70,
                "factual_accuracy": 70,
                "completeness": 70,
                "coherence": 70,
                "citation_quality": 70,
                "objectivity": 70,
                "readability": 70,
                "summary": f"Evaluation failed: {e}",
            }
