"""Token counting and cost calculation."""

from typing import Any

# Token prices (USD per 1K tokens) - claude-sonnet-4-20250514
PRICING = {
    "claude-sonnet-4-20250514": {"input": 0.003, "output": 0.015},
    "claude-3-5-sonnet-20241022": {"input": 0.003, "output": 0.015},
    "gpt-4o": {"input": 0.005, "output": 0.015},
    "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
}


def count_tokens(text: str, model: str = "claude-sonnet-4-20250514") -> int:
    """Estimate token count for text."""
    try:
        import tiktoken

        # Use cl100k_base for OpenAI models, fallback for others
        if "gpt" in model.lower():
            encoding = tiktoken.encoding_for_model(model)
        else:
            encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
    except Exception:
        # Fallback: ~4 chars per token
        return len(text) // 4


def calculate_cost(
    model: str, input_tokens: int, output_tokens: int
) -> float:
    """Calculate cost in USD for token usage."""
    pricing = PRICING.get(model, PRICING["claude-sonnet-4-20250514"])
    input_cost = (input_tokens / 1000) * pricing["input"]
    output_cost = (output_tokens / 1000) * pricing["output"]
    return round(input_cost + output_cost, 6)
