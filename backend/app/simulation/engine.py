"""
Teresa Simulation Engine
Runs parallel agent interactions and prediction simulation.
"""
import asyncio
import json
import random
import uuid
from datetime import datetime
from typing import Any, Optional

from ..agents.engine import AgentEngine
from ..core.config import get_settings
from ..models.agent import Agent, AgentInteraction
from ..models.simulation import (
    PredictionReport,
    SeedData,
    SeedType,
    Simulation,
    SimulationEvent,
    SimulationStatus,
)

settings = get_settings()


class SimulationEngine:
    """
    Core simulation engine for Teresa.
    Manages agent interactions, prediction synthesis, and real-time events.
    """

    def __init__(self, agent_engine: AgentEngine, memory_store):
        self.agent_engine = agent_engine
        self.memory_store = memory_store
        self.active_simulation: Optional[Simulation] = None
        self.event_queue: asyncio.Queue[SimulationEvent] = asyncio.Queue()
        self._stop_event = asyncio.Event()

    async def run_simulation(
        self,
        simulation: Simulation,
    ) -> Simulation:
        """Run a complete prediction simulation."""

        self.active_simulation = simulation
        simulation.status = SimulationStatus.RUNNING
        simulation.started_at = datetime.utcnow()

        await self._emit_event("simulation_started", {
            "simulation_id": simulation.id,
            "agent_count": simulation.agent_count,
        })

        try:
            # Phase 1: Agent initialization
            await self._initialize_agents(simulation)

            # Phase 2: Main simulation rounds
            for round_num in range(simulation.max_rounds):
                if self._stop_event.is_set():
                    break

                simulation.current_round = round_num + 1
                simulation.progress = (round_num + 1) / simulation.max_rounds

                await self._run_round(simulation, round_num + 1)

                await asyncio.sleep(settings.SIMULATION_STREAM_INTERVAL)

            # Phase 3: Consensus building
            await self._build_consensus(simulation)

            # Phase 4: Report generation
            report = await self._generate_report(simulation)
            simulation.prediction_report = report.prediction
            simulation.confidence_score = report.confidence
            simulation.status = SimulationStatus.COMPLETED
            simulation.completed_at = datetime.utcnow()

            await self._emit_event("simulation_completed", {
                "simulation_id": simulation.id,
                "prediction": report.prediction,
                "confidence": report.confidence,
            })

            return simulation

        except Exception as e:
            simulation.status = SimulationStatus.FAILED
            simulation.updated_at = datetime.utcnow()
            await self._emit_event("simulation_failed", {
                "simulation_id": simulation.id,
                "error": str(e),
            })
            raise

    async def _initialize_agents(self, simulation: Simulation) -> None:
        """Initialize agents with seed data."""

        await self._emit_event("agents_initializing", {
            "count": simulation.agent_count,
        })

        # Load agent config from simulation or use defaults
        role_dist = simulation.agent_config.get("role_distribution")
        agents = self.agent_engine.create_batch(
            count=simulation.agent_count,
            role_distribution=role_dist,
        )

        # Build social graph
        density = simulation.agent_config.get("connection_density", 0.1)
        self.agent_engine.build_social_graph(connection_density=density)

        # Inject seed knowledge into memory
        for agent in agents:
            await self.memory_store.add_episodic(
                agent_id=agent.id,
                content=f"Seed data: {simulation.seed_data.content}",
                importance=1.0,
            )

        await self._emit_event("agents_ready", {
            "count": len(agents),
        })

    async def _run_round(self, simulation: Simulation, round_num: int) -> None:
        """Run a single simulation round."""

        agents = self.agent_engine.get_all_agents()
        interactions_this_round = 0

        # Randomly select pairs to interact
        interactions_needed = int(len(agents) * 0.3)  # 30% of agents interact each round

        for _ in range(interactions_needed):
            agent_a = random.choice(agents)
            agent_b = random.choice(agents)

            if agent_a.id == agent_b.id:
                continue

            # Check if they have affinity
            affinity_a = agent_a.affinity_scores.get(agent_b.id, 0.5)
            if random.random() > affinity_a:
                # Low affinity interaction
                agent_b = random.choice(agents)

            await self._agent_interaction(simulation, agent_a, agent_b, round_num)
            interactions_this_round += 1

        simulation.total_interactions += interactions_this_round

        await self._emit_event("round_complete", {
            "simulation_id": simulation.id,
            "round": round_num,
            "interactions": interactions_this_round,
        })

    async def _agent_interaction(
        self,
        simulation: Simulation,
        agent_a: Agent,
        agent_b: Agent,
        round_num: int,
    ) -> AgentInteraction:
        """Simulate interaction between two agents."""

        # Get contexts
        context_a = await self.memory_store.get_agent_context(agent_a)
        context_b = await self.memory_store.get_agent_context(agent_b)

        # Simulate interaction outcome based on personalities
        interaction_type = self._determine_interaction_type(agent_a, agent_b)

        # Update working memories
        await self.memory_store.add_working_memory(
            agent_a.id,
            "last_interaction",
            {"with": agent_b.id, "type": interaction_type, "round": round_num},
        )

        await self.memory_store.add_working_memory(
            agent_b.id,
            "last_interaction",
            {"with": agent_a.id, "type": interaction_type, "round": round_num},
        )

        # Update energy and stats
        agent_a.rounds_participated += 1
        agent_b.rounds_participated += 1
        agent_a.energy = max(50.0, agent_a.energy - random.uniform(1.0, 3.0))
        agent_b.energy = max(50.0, agent_b.energy - random.uniform(1.0, 3.0))

        # Store episodic memory
        await self.memory_store.add_episodic(
            agent_a.id,
            f"Interacted with {agent_b.name} ({interaction_type})",
            importance=random.uniform(0.3, 0.8),
        )

        # Track interaction types
        sim_type_key = f"round_{interaction_type}"
        simulation.interaction_types[sim_type_key] = (
            simulation.interaction_types.get(sim_type_key, 0) + 1
        )

        # Update participation
        for agent in [agent_a, agent_b]:
            simulation.agent_participation[agent.id] = (
                simulation.agent_participation.get(agent.id, 0) + 1
            )

        interaction = AgentInteraction(
            agent_a_id=agent_a.id,
            agent_b_id=agent_b.id,
            interaction_type=interaction_type,
            content=f"{agent_a.name} and {agent_b.name} discussed {simulation.seed_data.type}",
            outcome=self._determine_outcome(agent_a, agent_b),
            confidence_delta_a=random.uniform(-0.1, 0.1),
            confidence_delta_b=random.uniform(-0.1, 0.1),
        )

        return interaction

    def _determine_interaction_type(self, a: Agent, b: Agent) -> str:
        """Determine interaction type based on personalities."""

        # High agreeableness -> dialogue/collaboration
        avg_agree = (a.personality.get("agreeableness", 0.5) +
                      b.personality.get("agreeableness", 0.5)) / 2

        # High openness -> innovation/breakthrough possible
        avg_open = (a.personality.get("openness", 0.5) +
                   b.personality.get("openness", 0.5)) / 2

        rand = random.random()

        if avg_agree > 0.7 and rand < 0.6:
            return "collaboration"
        elif avg_agree < 0.3 and rand < 0.5:
            return "conflict"
        elif avg_open > 0.8 and rand < 0.3:
            return "breakthrough"
        else:
            return "dialogue"

    def _determine_outcome(self, a: Agent, b: Agent) -> str:
        """Determine interaction outcome."""

        # Affinity based
        affinity = a.affinity_scores.get(b.id, 0.5)
        rand = random.random()

        if affinity > 0.7 and rand < 0.6:
            return "agreement"
        elif affinity < 0.3 and rand < 0.5:
            return "disagreement"
        else:
            return "neutral"

    async def _build_consensus(self, simulation: Simulation) -> None:
        """Build prediction consensus from all agent views."""

        agents = self.agent_engine.get_all_agents()

        # Collect "opinions" based on agent personalities
        opinions = {}
        for agent in agents:
            opinion = self._generate_agent_opinion(agent, simulation.seed_data)
            opinions[agent.id] = opinion

        # Find clusters of agreement
        simulation.consensus = self._cluster_opinions(opinions)

        await self._emit_event("consensus_built", {
            "simulation_id": simulation.id,
            "clusters": len(simulation.consensus),
        })

    def _generate_agent_opinion(self, agent: Agent, seed: SeedData) -> str:
        """Generate an opinion based on agent personality."""

        # In production, this would use LLM
        # For now, simulate based on personality

        openness = agent.personality.get("openness", 0.5)
        neuroticism = agent.personality.get("neuroticism", 0.5)

        if openness > 0.7:
            return "optimistic_outcome"
        elif neuroticism > 0.7:
            return "pessimistic_outcome"
        elif agent.role == "skeptic":
            return "skeptical_view"
        elif agent.role == "analyst":
            return "analytical_view"
        else:
            return "moderate_view"

    def _cluster_opinions(self, opinions: dict[str, str]) -> dict[str, float]:
        """Cluster opinions and calculate consensus probabilities."""

        # Count opinion types
        opinion_counts: dict[str, int] = {}
        for opinion in opinions.values():
            opinion_counts[opinion] = opinion_counts.get(opinion, 0) + 1

        # Convert to probabilities
        total = len(opinions)
        return {op: count / total for op, count in opinion_counts.items()}

    async def _generate_report(self, simulation: Simulation) -> PredictionReport:
        """Generate final prediction report."""

        # Synthesize from consensus and emergent patterns
        main_outcome = max(
            simulation.consensus.items(),
            key=lambda x: x[1],
        )
        prediction_text = self._format_prediction(main_outcome, simulation)

        confidence = main_outcome[1]
        confidence = min(0.95, confidence * 1.2)  # Boost for consensus

        report = PredictionReport(
            simulation_id=simulation.id,
            prediction=prediction_text,
            confidence=confidence,
            key_factors=[
                f"High agent consensus ({confidence:.0%})",
                f"{simulation.total_interactions} total interactions",
                f"{simulation.agent_count} agents participated",
            ],
            risk_assessment=self._assess_risk(confidence),
            alternative_scenarios=self._generate_alternatives(simulation),
            recommendations=[
                "Monitor for early indicators",
                "Prepare contingency plans",
                "Track agent sentiment evolution",
            ],
            supporting_evidence=[simulation.seed_data.content[:200]],
            method_notes=f"Teresa Swarm Intelligence v{settings.APP_VERSION}",
        )

        return report

    def _format_prediction(self, outcome: tuple, simulation: Simulation) -> str:
        """Format prediction as readable text."""

        outcome_type, probability = outcome
        seed_type = simulation.seed_data.type.value

        return f"""
Based on simulation of {simulation.agent_count} agents over {simulation.max_rounds} rounds,
Teresa predicts a {outcome_type.replace('_', ' ')} outcome with {probability:.0%} confidence.

The prediction is synthesized from {simulation.total_interactions} agent interactions
across {len(simulation.interaction_types)} interaction types.

Seed analysis: {seed_type}
Question: {simulation.prediction_question}
"""

    def _assess_risk(self, confidence: float) -> str:
        """Assess prediction risk level."""

        if confidence > 0.8:
            return "Low risk - high consensus"
        elif confidence > 0.6:
            return "Medium risk - moderate consensus"
        else:
            return "High risk - low consensus, monitor closely"

    def _generate_alternatives(self, simulation: Simulation) -> list[dict]:
        """Generate alternative scenarios."""

        alternatives = []
        for outcome, prob in simulation.consensus.items():
            if prob > 0.1 and outcome != max(simulation.consensus.items(), key=lambda x: x[1])[0]:
                alternatives.append({
                    "outcome": outcome,
                    "probability": prob,
                })

        return alternatives[:3]  # Top 3 alternatives

    async def _emit_event(self, event_type: str, data: dict) -> None:
        """Emit simulation event for streaming."""

        event = SimulationEvent(
            simulation_id=self.active_simulation.id if self.active_simulation else "unknown",
            event_type=event_type,
            data=data,
        )
        await self.event_queue.put(event)

    def stop(self) -> None:
        """Stop the simulation."""
        self._stop_event.set()

    async def get_events(self) -> list[SimulationEvent]:
        """Get pending events from queue."""
        events = []
        while not self.event_queue.empty():
            events.append(await self.event_queue.get())
        return events
