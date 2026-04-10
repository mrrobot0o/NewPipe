"""
Teresa Agent Model
Core agent entity with personality, memory, and behavior.
"""
from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field
from enum import Enum


class PersonalityDimension(str, Enum):
    """Personality dimensions for agents."""
    OPENNESS = "openness"
    CONSCIENTIOUSNESS = "conscientiousness"
    EXTRAVERSION = "extraversion"
    AGREEABLENESS = "agreeableness"
    NEUROTICISM = "neuroticism"


class AgentState(str, Enum):
    """Agent lifecycle states."""
    BORN = "born"
    ACTIVE = "active"
    DORMANT = "dormant"
    DECEASED = "deceased"


class Agent(BaseModel):
    """An intelligent agent with independent personality and memory."""

    # Identity
    id: str = Field(default_factory=lambda: f"agent_{datetime.now().timestamp_ns()}")
    name: str
    role: str  # e.g., "analyst", "critic", "optimist", "skeptic"
    avatar_url: Optional[str] = None

    # Personality (Big Five + custom)
    personality: dict[PersonalityDimension, float] = Field(
        default_factory=lambda: {
            PersonalityDimension.OPENNESS: 0.5,
            PersonalityDimension.CONSCIENTIOUSNESS: 0.5,
            PersonalityDimension.EXTRAVERSION: 0.5,
            PersonalityDimension.AGREEABLENESS: 0.5,
            PersonalityDimension.NEUROTICISM: 0.5,
        }
    )
    custom_traits: list[str] = Field(default_factory=list)

    # State
    state: AgentState = AgentState.BORN
    energy: float = 100.0
    influence: float = 1.0  # social impact multiplier
    reliability: float = 1.0  # track record

    # Memory
    episodic_memory: list[dict] = Field(default_factory=list)
    working_memory: dict[str, Any] = Field(default_factory=dict)

    # Relationships
    connections: list[str] = Field(default_factory=list)  # agent IDs
    affinity_scores: dict[str, float] = Field(default_factory=dict)  # agent_id -> score

    # Simulation
    rounds_participated: int = 0
    predictions_made: int = 0
    prediction_accuracy: float = 0.0

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_active: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class AgentInteraction(BaseModel):
    """Record of interaction between two agents."""

    id: str = Field(default_factory=lambda: f"interaction_{datetime.now().timestamp_ns()}")
    agent_a_id: str
    agent_b_id: str
    interaction_type: str  # "dialogue", "debate", "collaboration", "conflict"
    content: str
    outcome: str  # "agreement", "disagreement", "neutral", "breakthrough"
    confidence_delta_a: float
    confidence_delta_b: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)
