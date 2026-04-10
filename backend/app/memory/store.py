"""
Teresa Memory System
Three-tier memory: working, episodic, and vector-based semantic memory.
"""
import asyncio
import json
from datetime import datetime
from typing import Any, Optional, Union
from dataclasses import dataclass

from ..core.config import get_settings
from ..models.agent import Agent

settings = get_settings()


@dataclass
class MemoryEntry:
    """A single memory entry."""

    id: str
    agent_id: str
    memory_type: str  # "working", "episodic", "semantic"
    content: Union[str, dict]
    metadata: dict[str, Any]
    importance: float  # 0.0 to 1.0
    accessed_count: int
    created_at: datetime
    last_accessed: datetime
    embedding: Optional[list[float]] = None


class MemoryStore:
    """
    Three-tier memory system for agents.
    - Working memory: Fast, limited capacity, recent interactions
    - Episodic memory: Personal experiences over time
    - Semantic memory: Vector-based, shared knowledge
    """

    def __init__(self):
        # In-memory stores for demo (replace with real DB in production)
        self.working_memory: dict[str, dict[str, Any]] = {}
        self.episodic_memory: dict[str, list[MemoryEntry]] = {}
        self.semantic_memory: list[MemoryEntry] = []

        self.working_memory_limit = 20  # items per agent

    async def add_working_memory(
        self,
        agent_id: str,
        key: str,
        value: Any,
        ttl: int = 600,  # seconds
    ) -> None:
        """Add to working memory with TTL."""

        if agent_id not in self.working_memory:
            self.working_memory[agent_id] = {}

        limit = len(self.working_memory[agent_id])
        if limit >= self.working_memory_limit:
            # Evict oldest
            oldest_key = next(iter(self.working_memory[agent_id]))
            del self.working_memory[agent_id][oldest_key]

        self.working_memory[agent_id][key] = {
            "value": value,
            "expires_at": datetime.utcnow().timestamp() + ttl,
            "created_at": datetime.utcnow(),
        }

    async def get_working_memory(
        self,
        agent_id: str,
        key: Optional[str] = None,
    ) -> Optional[Union[Any, dict]]:
        """Get from working memory, evicting expired entries."""

        if agent_id not in self.working_memory:
            return None

        agent_mem = self.working_memory[agent_id]
        now = datetime.utcnow().timestamp()

        # Clean expired
        expired_keys = [k for k, v in agent_mem.items() if v["expires_at"] < now]
        for k in expired_keys:
            del agent_mem[k]

        if key:
            entry = agent_mem.get(key)
            return entry["value"] if entry else None

        return {k: v["value"] for k, v in agent_mem.items()}

    async def add_episodic(
        self,
        agent_id: str,
        content: Union[str, dict],
        importance: float = 0.5,
        metadata: Optional[dict] = None,
    ) -> str:
        """Add episodic memory entry."""

        memory_id = f"epi_{datetime.utcnow().timestamp_ns()}"

        entry = MemoryEntry(
            id=memory_id,
            agent_id=agent_id,
            memory_type="episodic",
            content=content,
            metadata=metadata or {},
            importance=importance,
            accessed_count=0,
            created_at=datetime.utcnow(),
            last_accessed=datetime.utcnow(),
        )

        if agent_id not in self.episodic_memory:
            self.episodic_memory[agent_id] = []

        self.episodic_memory[agent_id].append(entry)
        return memory_id

    async def get_episodic(
        self,
        agent_id: str,
        limit: int = 50,
        min_importance: float = 0.0,
    ) -> list[MemoryEntry]:
        """Get episodic memories for an agent."""

        if agent_id not in self.episodic_memory:
            return []

        memories = self.episodic_memory[agent_id]

        # Filter and sort by importance + recency
        filtered = [
            m
            for m in memories
            if m.importance >= min_importance
        ]
        filtered.sort(key=lambda m: m.importance, reverse=True)

        # Update access counts
        for m in filtered[:limit]:
            m.accessed_count += 1
            m.last_accessed = datetime.utcnow()

        return filtered[:limit]

    async def add_semantic(
        self,
        agent_id: str,
        content: str,
        importance: float = 0.5,
        embedding: Optional[list[float]] = None,
    ) -> str:
        """Add semantic memory with vector embedding."""

        memory_id = f"sem_{datetime.utcnow().timestamp_ns()}"

        entry = MemoryEntry(
            id=memory_id,
            agent_id=agent_id,
            memory_type="semantic",
            content=content,
            metadata={},
            importance=importance,
            accessed_count=0,
            created_at=datetime.utcnow(),
            last_accessed=datetime.utcnow(),
            embedding=embedding,
        )

        self.semantic_memory.append(entry)
        return memory_id

    async def semantic_search(
        self,
        query: str,
        limit: int = 10,
    ) -> list[MemoryEntry]:
        """Search semantic memory (simple keyword match for demo)."""

        query_lower = query.lower()
        results = []

        for entry in self.semantic_memory:
            if isinstance(entry.content, str):
                if query_lower in entry.content.lower():
                    score = entry.content.lower().count(query_lower) / len(entry.content)
                    results.append((entry, score))

        results.sort(key=lambda x: x[1], reverse=True)
        return [entry for entry, score in results[:limit]]

    async def consolidate(self, agent_id: str) -> None:
        """
        Consolidate episodic memories into semantic memory.
        Finds patterns and creates generalized knowledge.
        """
        episodic = await self.get_episodic(agent_id, limit=100)

        # Group by keywords
        grouped = {}
        for entry in episodic:
            content = (
                entry.content
                if isinstance(entry.content, str)
                else json.dumps(entry.content)
            )
            words = set(content.lower().split())
            for word in words:
                if word not in grouped:
                    grouped[word] = []
                grouped[word].append(entry)

        # Create consolidated entries for frequent patterns
        for word, entries in grouped.items():
            if len(entries) >= 3:
                # Pattern found
                importance = sum(e.importance for e in entries) / len(entries)
                consolidated = (
                    f"Pattern: '{word}' appears in {len(entries)} interactions. "
                    f"Average importance: {importance:.2f}"
                )
                await self.add_semantic(agent_id, consolidated, importance)

    async def get_agent_context(
        self,
        agent: Agent,
    ) -> str:
        """
        Get full memory context for an agent's prompt.
        Combines working, episodic, and relevant semantic memories.
        """
        working = await self.get_working_memory(agent.id)

        episodic = await self.get_episodic(agent.id, limit=5)
        episodic_str = "\n".join(
            f"- {m.created_at.strftime('%H:%M')}: {str(m.content)[:100]}..."
            for m in episodic
        )

        semantic = await self.semantic_search(f"agent {agent.id} personality {agent.role}", limit=3)
        semantic_str = "\n".join(
            f"- {m.content[:80]}..." for m in semantic
        )

        context = f"""
Working Memory:
{json.dumps(working, indent=2) if working else "(empty)"}

Recent Episodic Memory:
{episodic_str if episodic_str else "(empty)"}

Relevant Semantic Memory:
{semantic_str if semantic_str else "(empty)"}
"""
        return context

    def get_stats(self) -> dict[str, Any]:
        """Get memory system statistics."""

        total_episodic = sum(len(v) for v in self.episodic_memory.values())
        avg_episodic = total_episodic / len(self.episodic_memory) if self.episodic_memory else 0

        return {
            "working_memory_agents": len(self.working_memory),
            "total_episodic_entries": total_episodic,
            "avg_episodic_per_agent": avg_episodic,
            "total_semantic_entries": len(self.semantic_memory),
        }
