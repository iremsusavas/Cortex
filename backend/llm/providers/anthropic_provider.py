"""Anthropic Claude API provider."""

from typing import AsyncGenerator

from anthropic import AsyncAnthropic

from backend.llm.token_counter import count_tokens, calculate_cost


class AnthropicProvider:
    """Anthropic Claude API provider."""

    def __init__(self, api_key: str):
        self.client = AsyncAnthropic(api_key=api_key)

    async def complete(
        self,
        prompt: str,
        system: str = "",
        model: str = "claude-sonnet-4-20250514",
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> dict:
        """Complete a prompt and return full response."""
        input_tokens = count_tokens(system + prompt)
        response = await self.client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system if system else None,
            messages=[{"role": "user", "content": prompt}],
        )
        output_text = ""
        if response.content:
            for block in response.content:
                if hasattr(block, "text"):
                    output_text += block.text
        output_tokens = count_tokens(output_text)
        cost = calculate_cost(
            model, response.usage.input_tokens, response.usage.output_tokens
        )
        return {
            "content": output_text,
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
            "cost_usd": cost,
            "model": model,
        }

    async def stream(
        self,
        prompt: str,
        system: str = "",
        model: str = "claude-sonnet-4-20250514",
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> AsyncGenerator[str, None]:
        """Stream completion tokens."""
        async with self.client.messages.stream(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system if system else None,
            messages=[{"role": "user", "content": prompt}],
        ) as stream:
            async for text in stream.text_stream:
                yield text
