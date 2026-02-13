"""Provider-agnostic LLM abstraction layer with retry, cache, and cost tracking."""

import hashlib
import json
import logging
from typing import Any, AsyncGenerator

from backend.config import settings
from backend.llm.providers.anthropic_provider import AnthropicProvider
from backend.llm.providers.openai_provider import OpenAIProvider
from backend.llm.token_counter import calculate_cost, count_tokens

logger = logging.getLogger(__name__)


class LLMGateway:
    """
    Provider-agnostic LLM abstraction layer.

    Features:
    - Automatic retry with exponential backoff (3 attempts)
    - Response caching (Redis, TTL: 1 hour)
    - Token counting and cost calculation
    - Streaming support
    - Fallback: Anthropic -> OpenAI on rate limit
    """

    def __init__(self):
        self.anthropic = AnthropicProvider(api_key=settings.ANTHROPIC_API_KEY)
        self.openai = OpenAIProvider(api_key=settings.OPENAI_API_KEY)
        self._redis = None

    def _cache_key(self, model: str, system: str, prompt: str) -> str:
        """Generate cache key from request params."""
        content = f"{model}:{system}:{prompt}"
        return hashlib.sha256(content.encode()).hexdigest()

    async def _get_cache(self, key: str) -> dict | None:
        """Get from Redis cache."""
        try:
            if self._redis is None:
                import redis.asyncio as aioredis

                self._redis = aioredis.from_url(settings.REDIS_URL)
            cached = await self._redis.get(f"llm:{key}")
            if cached:
                return json.loads(cached)
        except Exception as e:
            logger.debug("Cache get failed: %s", e)
        return None

    async def _set_cache(self, key: str, value: dict, ttl: int = 3600) -> None:
        """Set Redis cache."""
        try:
            if self._redis is None:
                import redis.asyncio as aioredis

                self._redis = aioredis.from_url(settings.REDIS_URL)
            await self._redis.setex(
                f"llm:{key}",
                ttl,
                json.dumps(value),
            )
        except Exception as e:
            logger.debug("Cache set failed: %s", e)

    async def complete(
        self,
        prompt: str,
        system: str = "",
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        use_cache: bool = True,
    ) -> dict:
        """Complete a prompt with retry and optional cache."""
        model = model or settings.DEFAULT_MODEL
        temperature = temperature if temperature is not None else settings.TEMPERATURE
        max_tokens = max_tokens or settings.MAX_TOKENS_PER_AGENT

        if use_cache:
            cache_key = self._cache_key(model, system, prompt)
            cached = await self._get_cache(cache_key)
            if cached:
                return cached

        last_error = None
        use_anthropic = (
            settings.PRIMARY_LLM_PROVIDER == "anthropic"
            and "claude" in (model or "").lower()
        )
        for attempt in range(3):
            try:
                if use_anthropic and settings.ANTHROPIC_API_KEY:
                    result = await self.anthropic.complete(
                        prompt=prompt,
                        system=system,
                        model=model,
                        temperature=temperature,
                        max_tokens=max_tokens,
                    )
                else:
                    openai_model = "gpt-4o" if "claude" in (model or "").lower() else model
                    result = await self.openai.complete(
                        prompt=prompt,
                        system=system,
                        model=openai_model,
                        temperature=temperature,
                        max_tokens=max_tokens,
                    )
                if use_cache:
                    await self._set_cache(cache_key, result)
                return result
            except Exception as e:
                last_error = e
                err_str = str(e).lower()
                should_fallback = (
                    settings.OPENAI_API_KEY
                    and ("rate" in err_str or "credit" in err_str or "balance" in err_str)
                )
                if should_fallback:
                    # Fallback to OpenAI (rate limit, low credits, etc.)
                    try:
                        result = await self.openai.complete(
                            prompt=prompt,
                            system=system,
                            model="gpt-4o",
                            temperature=temperature,
                            max_tokens=max_tokens,
                        )
                        return result
                    except Exception:
                        pass
                wait_time = 2**attempt
                logger.warning("LLM attempt %d failed, retrying in %ds: %s", attempt + 1, wait_time, e)
                import asyncio

                await asyncio.sleep(wait_time)

        raise last_error or RuntimeError("LLM call failed")

    async def stream(
        self,
        prompt: str,
        system: str = "",
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> AsyncGenerator[str, None]:
        """Stream completion tokens."""
        model = model or settings.DEFAULT_MODEL
        temperature = temperature if temperature is not None else settings.TEMPERATURE
        max_tokens = max_tokens or settings.MAX_TOKENS_PER_AGENT

        try:
            if "claude" in model.lower():
                async for chunk in self.anthropic.stream(
                    prompt=prompt,
                    system=system,
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                ):
                    yield chunk
            else:
                async for chunk in self.openai.stream(
                    prompt=prompt,
                    system=system,
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                ):
                    yield chunk
        except Exception as e:
            if "rate" in str(e).lower() and settings.OPENAI_API_KEY:
                async for chunk in self.openai.stream(
                    prompt=prompt,
                    system=system,
                    model="gpt-4o",
                    temperature=temperature,
                    max_tokens=max_tokens,
                ):
                    yield chunk
            else:
                raise

    async def complete_json(
        self,
        prompt: str,
        system: str = "",
        model: str | None = None,
        temperature: float = 0.1,
        max_tokens: int | None = None,
    ) -> tuple[dict[str, Any], dict[str, float | int]]:
        """Complete with JSON output. Returns (parsed_data, usage_dict with cost_usd, input_tokens, output_tokens)."""
        system = system + "\n\nRespond with valid JSON only. No markdown, no code blocks."
        result = await self.complete(
            prompt=prompt,
            system=system,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens or 4096,
        )
        content = result["content"].strip()
        # Remove markdown code blocks if present
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        parsed = json.loads(content)
        usage = {
            "cost_usd": result.get("cost_usd", 0),
            "input_tokens": result.get("input_tokens", 0),
            "output_tokens": result.get("output_tokens", 0),
        }
        return parsed, usage
