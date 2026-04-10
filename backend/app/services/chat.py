"""
Teresa Agent Chat Service
Enables real-time conversations with agents using LLM.
"""
import asyncio
import json
from datetime import datetime
from typing import Any, Optional

from ..agents.engine import AgentEngine
from ..memory.store import MemoryStore
from ..models.agent import Agent
from ..models.simulation import Simulation
from ..services.llm import LLMService, get_llm_service


class AgentChatService:
    """
    Manages conversations between users and agents.
    Provides deep interaction capabilities.
    """

    def __init__(
        self,
        agent_engine: AgentEngine,
        memory_store: MemoryStore,
    ):
        self.agent_engine = agent_engine
        self.memory_store = memory_store
        self.conversation_history: dict[str, list[dict]] = {}
        self.llm: Optional[LLMService] = None

    def _get_llm(self) -> LLMService:
        """Lazily initialize LLM service."""
        if self.llm is None:
            self.llm = get_llm_service()
        return self.llm

    async def chat_with_agent(
        self,
        agent_id: str,
        user_message: str,
        simulation_context: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Send a message to an agent and get an intelligent response.

        Returns:
            Dict with agent response, metadata, and updated state.
        """
        agent = self.agent_engine.get_agent(agent_id)
        if not agent:
            return {"error": "Agent not found"}

        # Get agent memory context
        memory_context = await self.memory_store.get_agent_context(agent)

        # Build full context
        full_context = f"Agent's Memory:\n{memory_context}"
        if simulation_context:
            full_context += f"\n\nSimulation Context:\n{simulation_context}"

        # Add conversation history
        history = self.conversation_history.get(agent_id, [])
        history_str = ""
        if history:
            last_5 = history[-5:]
            history_str = "\n".join(
                f"{'User' if h['role'] == 'user' else agent.name}: {h['content']}"
                for h in last_5
            )
            full_context += f"\n\nRecent Conversation:\n{history_str}"

        # Generate response via LLM
        llm = self._get_llm()
        try:
            response_text = await llm.generate_agent_response(
                agent_name=agent.name,
                agent_role=agent.role,
                personality=agent.personality,
                context=full_context,
                user_message=user_message,
            )
        except Exception as e:
            response_text = f"[Error generating response: {str(e)}]"

        # Update conversation history
        if agent_id not in self.conversation_history:
            self.conversation_history[agent_id] = []

        self.conversation_history[agent_id].append({
            "role": "user",
            "content": user_message,
            "timestamp": datetime.utcnow().isoformat(),
        })
        self.conversation_history[agent_id].append({
            "role": "assistant",
            "content": response_text,
            "timestamp": datetime.utcnow().isoformat(),
        })

        # Update agent memory with this interaction
        await self.memory_store.add_episodic(
            agent_id=agent.id,
            content=f"User asked: '{user_message[:50]}...' | I responded with my {agent.role} perspective",
            importance=0.6,
        )

        # Update working memory
        await self.memory_store.add_working_memory(
            agent_id=agent.id,
            key="last_user_interaction",
            value={
                "user_message": user_message[:100],
                "my_response": response_text[:100],
            },
        )

        # Update agent state
        agent.last_active = datetime.utcnow()

        return {
            "agent_id": agent.id,
            "agent_name": agent.name,
            "agent_role": agent.role,
            "response": response_text,
            "personality": {k.value: v for k, v in agent.personality.items()},
            "energy": agent.energy,
            "interactions": agent.rounds_participated,
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def batch_chat(
        self,
        agent_ids: list[str],
        message: str,
        simulation_context: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """
        Send same message to multiple agents simultaneously.
        Useful for gauging group sentiment.
        """
        tasks = [
            self.chat_with_agent(aid, message, simulation_context)
            for aid in agent_ids
        ]

        responses = await asyncio.gather(*tasks, return_exceptions=True)

        results = []
        for resp in responses:
            if isinstance(resp, Exception):
                results.append({"error": str(resp)})
            else:
                results.append(resp)

        return results

    async def agent_debate(
        self,
        agent_a_id: str,
        agent_b_id: str,
        topic: str,
        rounds: int = 3,
    ) -> list[dict[str, Any]]:
        """
        Simulate a debate between two agents on a topic.
        """
        debate_history = []

        message_a = f"What is your position on: {topic}? State your view clearly."
        resp_a = await self.chat_with_agent(agent_a_id, message_a)
        debate_history.append({"agent": resp_a["agent_name"], "response": resp_a["response"]})

        for round_num in range(rounds):
            # Agent B responds to A
            message_b = f"{resp_a['agent_name']} said: \"{resp_a['response'][:200]}\". Respond with your counter-argument."
            resp_b = await self.chat_with_agent(agent_b_id, message_b)
            debate_history.append({"agent": resp_b["agent_name"], "response": resp_b["response"]})

            # Agent A responds to B
            message_a = f"{resp_b['agent_name']} said: \"{resp_b['response'][:200]}\". Respond with your counter-argument."
            resp_a = await self.chat_with_agent(agent_a_id, message_a)
            debate_history.append({"agent": resp_a["agent_name"], "response": resp_a["response"]})

        return debate_history

    def get_conversation_history(
        self,
        agent_id: str,
        limit: int = 20,
    ) -> list[dict]:
        """Get conversation history for an agent."""
        history = self.conversation_history.get(agent_id, [])
        return history[-limit:]

    def clear_history(self, agent_id: str) -> None:
        """Clear conversation history for an agent."""
        if agent_id in self.conversation_history:
            del self.conversation_history[agent_id]
