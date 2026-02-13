"""OpenAI GPT API provider (fallback)."""

from typing import AsyncGenerator

from openai import AsyncOpenAI

from backend.llm.token_counter import calculate_cost, count_tokens


class OpenAIProvider:
    """OpenAI GPT API provider."""

    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key) if api_key else None

    async def complete(
        self,
        prompt: str,
        system: str = "",
        model: str = "gpt-4o",
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> dict:
        """Complete a prompt and return full response."""
        if not self.client:
            raise ValueError("OpenAI API key not configured")
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        response = await self.client.chat.completions.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=messages,
        )
        output_text = response.choices[0].message.content or ""
        input_tokens = response.usage.prompt_tokens if response.usage else 0
        output_tokens = response.usage.completion_tokens if response.usage else 0
        cost = calculate_cost(model, input_tokens, output_tokens)
        return {
            "content": output_text,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost_usd": cost,
            "model": model,
        }

    async def stream(
        self,
        prompt: str,
        system: str = "",
        model: str = "gpt-4o",
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> AsyncGenerator[str, None]:
        """Stream completion tokens."""
        if not self.client:
            raise ValueError("OpenAI API key not configured")
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        stream = await self.client.chat.completions.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=messages,
            stream=True,
        )
        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
