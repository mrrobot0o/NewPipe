"""
Teresa Agent Engine
Creates and manages intelligent agents with distinct personalities.
"""
import json
import random
import uuid
from datetime import datetime
from typing import Any, Optional

from ..core.config import get_settings
from ..models.agent import (
    Agent,
    AgentInteraction,
    AgentState,
    PersonalityDimension,
)

settings = get_settings()

# Role templates with personality biases
ROLE_TEMPLATES = {
    "analyst": {
        "personality": {
            PersonalityDimension.OPENNESS: 0.7,
            PersonalityDimension.CONSCIENTIOUSNESS: 0.9,
            PersonalityDimension.EXTRAVERSION: 0.3,
            PersonalityDimension.AGREEABLENESS: 0.5,
            PersonalityDimension.NEUROTICISM: 0.3,
        },
        "traits": ["data-driven", "methodical", "skeptical", "precise"],
    },
    "optimist": {
        "personality": {
            PersonalityDimension.OPENNESS: 0.8,
            PersonalityDimension.CONSCIENTIOUSNESS: 0.5,
            PersonalityDimension.EXTRAVERSION: 0.8,
            PersonalityDimension.AGREEABLENESS: 0.7,
            PersonalityDimension.NEUROTICISM: 0.2,
        },
        "traits": ["hopeful", "creative", "risk-taking", "enthusiastic"],
    },
    "skeptic": {
        "personality": {
            PersonalityDimension.OPENNESS: 0.3,
            PersonalityDimension.CONSCIENTIOUSNESS: 0.8,
            PersonalityDimension.EXTRAVERSION: 0.4,
            PersonalityDimension.AGREEABLENESS: 0.2,
            PersonalityDimension.NEUROTICISM: 0.7,
        },
        "traits": ["critical", "cautious", "demanding", "thorough"],
    },
    "innovator": {
        "personality": {
            PersonalityDimension.OPENNESS: 0.95,
            PersonalityDimension.CONSCIENTIOUSNESS: 0.4,
            PersonalityDimension.EXTRAVERSION: 0.6,
            PersonalityDimension.AGREEABLENESS: 0.6,
            PersonalityDimension.NEUROTICISM: 0.4,
        },
        "traits": ["visionary", "unconventional", "curious", "disruptive"],
    },
    "pragmatist": {
        "personality": {
            PersonalityDimension.OPENNESS: 0.5,
            PersonalityDimension.CONSCIENTIOUSNESS: 0.9,
            PersonalityDimension.EXTRAVERSION: 0.5,
            PersonalityDimension.AGREEABLENESS: 0.6,
            PersonalityDimension.NEUROTICISM: 0.4,
        },
        "traits": ["practical", "realistic", "efficient", "results-oriented"],
    },
    "critic": {
        "personality": {
            PersonalityDimension.OPENNESS: 0.6,
            PersonalityDimension.CONSCIENTIOUSNESS: 0.7,
            PersonalityDimension.EXTRAVERSION: 0.3,
            PersonalityDimension.AGREEABLENESS: 0.3,
            PersonalityDimension.NEUROTICISM: 0.6,
        },
        "traits": ["sharp", "detail-oriented", "challenging", "perceptive"],
    },
    "diplomat": {
        "personality": {
            PersonalityDimension.OPENNESS: 0.6,
            PersonalityDimension.CONSCIENTIOUSNESS: 0.7,
            PersonalityDimension.EXTRAVERSION: 0.8,
            PersonalityDimension.AGREEABLENESS: 0.9,
            PersonalityDimension.NEUROTICISM: 0.3,
        },
        "traits": ["mediating", "empathetic", "persuasive", "balanced"],
    },
    "visionary": {
        "personality": {
            PersonalityDimension.OPENNESS: 0.95,
            PersonalityDimension.CONSCIENTIOUSNESS: 0.3,
            PersonalityDimension.EXTRAVERSION: 0.7,
            PersonalityDimension.AGREEABLENESS: 0.5,
            PersonalityDimension.NEUROTICISM: 0.5,
        },
        "traits": ["big-picture", "inspiring", "abstract-thinker", "future-oriented"],
    },
}

# Name pools for agent generation
FIRST_NAMES = [
    "Ada", "Alan", "Grace", "Claude", "Sofia", "Marcus", "Yuki", "Omar",
    "Elena", "Raj", "Nina", "Leo", "Mia", "Felix", "Zara", "Hugo",
    "Lina", "Dante", "Aria", "Kai", "Nova", "Atlas", "Luna", "Phoenix",
    "Sage", "River", "Ember", "Storm", "Jade", "Raven", "Echo", "Blaze",
    "Iris", "Quinn", "Vera", "Orion", "Lyra", "Cass", "Nyx", "Solaris",
]

LAST_NAMES = [
    "Chen", "Patel", "Silva", "Novak", "Kim", "Reyes", "Müller", "Tanaka",
    "Okafor", "Larsson", "Dubois", "Singh", "Santos", "Fischer", "Park",
    "Ahmed", "Torres", "Johansson", "Nakamura", "Costa", "Volkov", "Shah",
    "Andersson", "Moreau", "Takahashi", "Berg", "Rao", "Lund", "Voss", "Shaw",
]


class AgentEngine:
    """
    Creates and manages agents with rich personalities.
    Supports batch creation, persona injection, and social graph building.
    """

    def __init__(self):
        self.agents: dict[str, Agent] = {}
        self.role_templates = ROLE_TEMPLATES

    def create_agent(
        self,
        name: Optional[str] = None,
        role: Optional[str] = None,
        personality_override: Optional[dict] = None,
        custom_traits: Optional[list[str]] = None,
    ) -> Agent:
        """Create a single agent with personality."""

        role = role or random.choice(list(self.role_templates.keys()))
        template = self.role_templates.get(role, self.role_templates["analyst"])

        name = name or f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"

        # Base personality from template with randomization
        personality = {}
        for dim, base_val in template["personality"].items():
            # Add ±0.2 random variation
            personality[dim] = max(0.0, min(1.0, base_val + random.uniform(-0.2, 0.2)))

        # Apply overrides
        if personality_override:
            for k, v in personality_override.items():
                if isinstance(k, PersonalityDimension):
                    personality[k] = v

        agent = Agent(
            id=f"agent_{uuid.uuid4().hex[:12]}",
            name=name,
            role=role,
            personality=personality,
            custom_traits=custom_traits or template["traits"].copy(),
            state=AgentState.ACTIVE,
        )

        self.agents[agent.id] = agent
        return agent

    def create_batch(
        self,
        count: int,
        role_distribution: Optional[dict[str, float]] = None,
    ) -> list[Agent]:
        """Create a batch of agents with role distribution."""

        if role_distribution is None:
            # Equal distribution across all roles
            roles = list(self.role_templates.keys())
            role_distribution = {r: 1.0 / len(roles) for r in roles}

        agents = []
        for _ in range(count):
            role = random.choices(
                list(role_distribution.keys()),
                weights=list(role_distribution.values()),
                k=1,
            )[0]
            agents.append(self.create_agent(role=role))

        return agents

    def build_social_graph(self, connection_density: float = 0.1) -> None:
        """Build initial social connections between agents."""

        agent_list = list(self.agents.values())
        n = len(agent_list)

        for i, agent in enumerate(agent_list):
            for j in range(i + 1, n):
                if random.random() < connection_density:
                    other = agent_list[j]

                    # Calculate affinity based on personality similarity
                    affinity = self._calculate_affinity(agent, other)

                    agent.connections.append(other.id)
                    other.connections.append(agent.id)
                    agent.affinity_scores[other.id] = affinity
                    other.affinity_scores[agent.id] = affinity

    def _calculate_affinity(self, a: Agent, b: Agent) -> float:
        """Calculate affinity between two agents based on personality."""

        similarity = 0.0
        dims = list(a.personality.keys())

        for dim in dims:
            diff = abs(a.personality[dim] - b.personality.get(dim, 0.5))
            similarity += 1.0 - diff

        # Opposites attract factor (small bonus for complementary traits)
        complement = 0.0
        for dim in dims:
            complement += abs(a.personality[dim] - b.personality.get(dim, 0.5))
        complement = min(complement / len(dims), 0.5) * 0.2  # Small bonus

        return (similarity / len(dims)) + complement

    def get_agent(self, agent_id: str) -> Optional[Agent]:
        return self.agents.get(agent_id)

    def get_all_agents(self) -> list[Agent]:
        return list(self.agents.values())

    def get_agents_by_role(self, role: str) -> list[Agent]:
        return [a for a in self.agents.values() if a.role == role]

    def to_prompt_context(self, agent: Agent) -> str:
        """Convert agent to a prompt-friendly context string."""

        personality_desc = ", ".join(
            f"{dim.value}: {val:.1f}" for dim, val in agent.personality.items()
        )

        return (
            f"Agent: {agent.name} (Role: {agent.role})\n"
            f"Personality: [{personality_desc}]\n"
            f"Traits: {', '.join(agent.custom_traits)}\n"
            f"Energy: {agent.energy:.0f}%, Influence: {agent.influence:.1f}\n"
            f"Rounds participated: {agent.rounds_participated}"
        )
