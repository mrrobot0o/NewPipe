"""
Teresa Simulation Model
Manages prediction simulations with multiple agents.
"""
from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field
from enum import Enum


class SimulationStatus(str, Enum):
    """Simulation lifecycle states."""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class SeedType(str, Enum):
    """Types of seed data."""
    TEXT_REPORT = "text_report"
    NEWS_ARTICLE = "news_article"
    POLICY_DRAFT = "policy_draft"
    FINANCIAL_DATA = "financial_data"
    NOVEL_STORY = "novel_story"
    CUSTOM = "custom"


class SeedData(BaseModel):
    """Seed information to initialize a simulation."""

    id: str
    type: SeedType
    content: str
    source_url: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    extracted_at: datetime = Field(default_factory=datetime.utcnow)


class Simulation(BaseModel):
    """A complete prediction simulation with agents."""

    # Identity
    id: str = Field(default_factory=lambda: f"sim_{datetime.now().timestamp_ns()}")
    title: str
    description: str

    # Configuration
    seed_data: SeedData
    prediction_question: str  # What are we predicting?
    agent_count: int = 100
    max_rounds: int = 40
    agent_config: dict[str, Any] = Field(default_factory=dict)

    # State
    status: SimulationStatus = SimulationStatus.PENDING
    current_round: int = 0
    progress: float = 0.0

    # Results
    prediction_report: Optional[str] = None
    confidence_score: Optional[float] = None
    consensus: Optional[dict[str, float]] = None  # outcome -> probability
    emergent_patterns: list[dict] = Field(default_factory=list)

    # Analytics
    total_interactions: int = 0
    interaction_types: dict[str, int] = Field(default_factory=dict)
    agent_participation: dict[str, int] = Field(default_factory=dict)
    sentiment_evolution: list[dict] = Field(default_factory=list)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class SimulationEvent(BaseModel):
    """Real-time event from simulation for streaming."""

    id: str = Field(default_factory=lambda: f"event_{datetime.now().timestamp_ns()}")
    simulation_id: str
    event_type: str  # "round_complete", "agent_speak", "consensus_shift", etc.
    data: dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class PredictionReport(BaseModel):
    """Final prediction report with analysis."""

    simulation_id: str
    prediction: str  # main prediction text
    confidence: float  # 0.0 to 1.0
    key_factors: list[str]
    risk_assessment: str
    alternative_scenarios: list[dict[str, Any]]
    recommendations: list[str]
    supporting_evidence: list[str]
    method_notes: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)
