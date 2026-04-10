"""
Teresa LLM Service
Manages connections to OpenAI-compatible APIs for agent intelligence.
"""
import asyncio
import json
import hashlib
from typing import Any, Optional

from openai import AsyncOpenAI
from ..core.config import get_settings

settings = get_settings()


class LLMCache:
    """Simple in-memory cache for LLM responses."""

    def __init__(self, max_size: int = 1000):
        self.cache: dict[str, dict[str, Any]] = {}
        self.max_size = max_size
        self.access_order: list[str] = []

    def _generate_key(self, messages: list[dict]) -> str:
        """Generate cache key from messages."""
        content = json.dumps(messages, sort_keys=True)
        return hashlib.md5(content.encode()).hexdigest()

    def get(self, messages: list[dict]) -> Optional[str]:
        """Get cached response if available."""
        key = self._generate_key(messages)

        if key in self.cache:
            entry = self.cache[key]
            entry["access_count"] += 1
            entry["last_accessed"] = asyncio.get_event_loop().time()

            # Move to end of access order
            if key in self.access_order:
                self.access_order.remove(key)
            self.access_order.append(key)

            return entry["response"]

        return None

    def set(self, messages: list[dict], response: str, model: str) -> None:
        """Cache LLM response."""
        key = self._generate_key(messages)

        # Evict if full
        if len(self.cache) >= self.max_size:
            oldest_key = self.access_order.pop(0)
            del self.cache[oldest_key]

        self.cache[key] = {
            "messages": messages,
            "response": response,
            "model": model,
            "created_at": asyncio.get_event_loop().time(),
            "access_count": 0,
        }
        self.access_order.append(key)

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        hit_count = sum(e["access_count"] for e in self.cache.values())
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "total_hits": hit_count,
            "hit_rate": hit_count / max(hit_count + 1, 1),
        }


class LLMService:
    """
    Service for interacting with LLM APIs.
    Supports OpenAI-compatible providers (OpenAI, Anthropic, etc.).
    """

    def __init__(self):
        if not settings.LLM_API_KEY:
            raise ValueError("LLM_API_KEY not configured")

        self.client = AsyncOpenAI(
            api_key=settings.LLM_API_KEY,
            base_url=settings.LLM_BASE_URL,
        )

        self.cache = LLMCache(max_size=1000)
        self.model = settings.LLM_MODEL_NAME

    async def chat(
        self,
        messages: list[dict],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        use_cache: bool = True,
    ) -> str:
        """
        Send chat completion request to LLM.

        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            use_cache: Whether to use response cache

        Returns:
            LLM response text
        """
        if use_cache:
            cached = self.cache.get(messages)
            if cached:
                return cached

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature or settings.LLM_TEMPERATURE,
            max_tokens=max_tokens or settings.LLM_MAX_TOKENS,
        )

        result = response.choices[0].message.content

        if use_cache:
            self.cache.set(messages, result, self.model)

        return result

    async def generate_agent_response(
        self,
        agent_name: str,
        agent_role: str,
        personality: dict[str, float],
        context: str,
        user_message: str,
    ) -> str:
        """
        Generate a personality-aware response for an agent.

        Args:
            agent_name: Name of the agent
            agent_role: Role (analyst, optimist, etc.)
            personality: Big Five personality scores
            context: Agent's memory context
            user_message: Message to respond to

        Returns:
            Agent's response text
        """
        system_prompt = self._build_personality_prompt(
            agent_name,
            agent_role,
            personality,
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Context:\n{context}\n\nUser message:\n{user_message}"},
        ]

        response = await self.chat(messages, temperature=0.8)

        return response

    def _build_personality_prompt(
        self,
        name: str,
        role: str,
        personality: dict[str, float],
    ) -> str:
        """Build system prompt incorporating personality."""

        # Convert personality scores to descriptions
        traits = []
        for dim, value in personality.items():
            if value >= 0.8:
                traits.append(f"very high {dim}")
            elif value >= 0.6:
                traits.append(f"high {dim}")
            elif value <= 0.2:
                traits.append(f"very low {dim}")
            elif value <= 0.4:
                traits.append(f"low {dim}")

        role_instructions = {
            "analyst": "You are data-driven and analytical. You base responses on evidence and logic.",
            "optimist": "You are hopeful and see opportunities. You focus on positive outcomes.",
            "skeptic": "You are critical and cautious. You question assumptions and demand proof.",
            "innovator": "You are creative and unconventional. You propose novel solutions.",
            "pragmatist": "You are practical and realistic. You focus on what works.",
            "critic": "You are sharp and detail-oriented. You challenge weak points.",
            "diplomat": "You are empathetic and balanced. You seek understanding between views.",
            "visionary": "You are big-picture focused. You think about long-term impact.",
        }

        instruction = role_instructions.get(role, "You are a helpful AI assistant.")

        prompt = f"""You are {name}, a {role} agent in a swarm intelligence system.

Your personality traits (Big Five model):
{chr(10).join(f'- {t}' for t in traits)}

Your role characteristics:
{instruction}

Guidelines:
- Stay in character as {name} with your specific personality
- Draw from the context provided (your memory and recent interactions)
- Be concise but thoughtful
- Show your role's unique perspective
- Do not break character or become generic

Respond naturally as {name} would in a group discussion."""
        return prompt

    async def generate_prediction_report(
        self,
        prediction: str,
        confidence: float,
        factors: list[str],
        scenarios: list[dict],
    ) -> str:
        """Generate formatted prediction report using LLM."""

        prompt = f"""Generate a professional prediction report based on the following analysis:

Prediction: {prediction}
Confidence: {confidence:.1%}
Key Factors:
{chr(10).join(f'- {f}' for f in factors)}

Alternative Scenarios:
{chr(10).join(f"- {s['outcome']}: {s['probability']:.0%}" for s in scenarios)}

Create a well-structured report with:
1. Executive Summary
2. Detailed Analysis
3. Risk Assessment
4. Recommendations
5. Conclusion

Use professional, analytical language suitable for decision-makers."""

        response = await self.chat([{"role": "user", "content": prompt}], temperature=0.5)

        return response

    def get_cache_stats(self) -> dict[str, Any]:
        """Get LLM cache statistics."""
        return self.cache.get_stats()


# Global LLM service instance
_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """Get or create global LLM service instance."""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
