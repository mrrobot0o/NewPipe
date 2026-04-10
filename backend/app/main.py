"""
Teresa API - Main FastAPI Application
"""
import asyncio
import json
import uuid
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .agents.engine import AgentEngine
from .memory.store import MemoryStore
from .simulation.engine import SimulationEngine
from .models.simulation import (
    PredictionReport,
    SeedData,
    SeedType,
    Simulation,
    SimulationStatus,
)

from .services.chat import AgentChatService


# --- App Setup ---
app = FastAPI(
    title="Teresa - Swarm Intelligence Engine",
    description="Next-generation AI prediction engine powered by multi-agent technology",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Global State ---
agent_engine = AgentEngine()
memory_store = MemoryStore()
sim_engine = SimulationEngine(agent_engine, memory_store)
simulations: dict[str, Simulation] = {}
chat_service = AgentChatService(agent_engine, memory_store)


# --- Request Models ---
class CreateSimulationRequest(BaseModel):
    title: str
    description: str
    seed_content: str
    seed_type: SeedType = SeedType.CUSTOM
    prediction_question: str
    agent_count: int = 100
    max_rounds: int = 40
    role_distribution: Optional[dict[str, float]] = None
    connection_density: float = 0.1


class ChatRequest(BaseModel):
    simulation_id: Optional[str] = None
    agent_id: str
    message: str


class BatchChatRequest(BaseModel):
    agent_ids: list[str]
    message: str
    simulation_id: Optional[str] = None


class DebateRequest(BaseModel):
    agent_a_id: str
    agent_b_id: str
    topic: str
    rounds: int = 3


# --- Endpoints ---

@app.get("/")
async def root():
    return {
        "name": "Teresa",
        "version": "0.1.0",
        "description": "Next-Gen Swarm Intelligence Engine",
        "status": "running",
    }


@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


# --- Simulation Endpoints ---

@app.post("/api/v1/simulations", response_model=Simulation)
async def create_simulation(req: CreateSimulationRequest):
    """Create a new prediction simulation."""

    seed = SeedData(
        id=f"seed_{uuid.uuid4().hex[:12]}",
        type=req.seed_type,
        content=req.seed_content,
    )

    simulation = Simulation(
        id=f"sim_{uuid.uuid4().hex[:12]}",
        title=req.title,
        description=req.description,
        seed_data=seed,
        prediction_question=req.prediction_question,
        agent_count=req.agent_count,
        max_rounds=req.max_rounds,
        agent_config={
            "role_distribution": req.role_distribution,
            "connection_density": req.connection_density,
        },
    )

    simulations[simulation.id] = simulation
    return simulation


@app.post("/api/v1/simulations/{sim_id}/run")
async def run_simulation(sim_id: str):
    """Start running a simulation."""

    if sim_id not in simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")

    sim = simulations[sim_id]

    if sim.status == SimulationStatus.RUNNING:
        raise HTTPException(status_code=400, detail="Simulation already running")

    # Run in background
    asyncio.create_task(sim_engine.run_simulation(sim))

    return {"status": "started", "simulation_id": sim_id}


@app.post("/api/v1/simulations/{sim_id}/stop")
async def stop_simulation(sim_id: str):
    """Stop a running simulation."""

    if sim_id not in simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")

    sim_engine.stop()
    return {"status": "stopping", "simulation_id": sim_id}


@app.get("/api/v1/simulations/{sim_id}", response_model=Simulation)
async def get_simulation(sim_id: str):
    """Get simulation details."""

    if sim_id not in simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")

    return simulations[sim_id]


@app.get("/api/v1/simulations", response_model=list[Simulation])
async def list_simulations():
    """List all simulations."""

    return list(simulations.values())


@app.get("/api/v1/simulations/{sim_id}/report", response_model=PredictionReport)
async def get_report(sim_id: str):
    """Get prediction report for a completed simulation."""

    if sim_id not in simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")

    sim = simulations[sim_id]

    if sim.status != SimulationStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Simulation not yet completed")

    return PredictionReport(
        simulation_id=sim.id,
        prediction=sim.prediction_report,
        confidence=sim.confidence_score,
        key_factors=[],
        risk_assessment="",
        alternative_scenarios=[],
        recommendations=[],
        supporting_evidence=[],
        method_notes=f"Teresa v0.1.0",
    )


# --- Agent Endpoints ---

@app.get("/api/v1/agents")
async def list_agents(role: Optional[str] = None):
    """List all agents, optionally filtered by role."""

    if role:
        return agent_engine.get_agents_by_role(role)
    return agent_engine.get_all_agents()


@app.get("/api/v1/agents/{agent_id}")
async def get_agent(agent_id: str):
    """Get agent details."""

    agent = agent_engine.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    return agent


@app.post("/api/v1/agents/{agent_id}/chat")
async def chat_with_agent(req: ChatRequest):
    """Chat with a specific agent using LLM."""

    response = await chat_service.chat_with_agent(
        agent_id=req.agent_id,
        user_message=req.message,
        simulation_context=req.simulation_id,
    )

    return response


@app.post("/api/v1/agents/batch-chat")
async def batch_chat(req: BatchChatRequest):
    """Send message to multiple agents."""

    responses = await chat_service.batch_chat(
        agent_ids=req.agent_ids,
        message=req.message,
        simulation_context=req.simulation_id,
    )

    return {"responses": responses}



@app.post("/api/v1/agents/debate")
async def agent_debate(req: DebateRequest):
    """Simulate a debate between two agents."""

    debate_history = await chat_service.agent_debate(
        agent_a_id=req.agent_a_id,
        agent_b_id=req.agent_b_id,
        topic=req.topic,
        rounds=req.rounds,
    )

    return {"debate": debate_history}



@app.get("/api/v1/agents/{agent_id}/history")
async def get_agent_history(agent_id: str, limit: int = 20):
    """Get conversation history for an agent."""

    return chat_service.get_conversation_history(agent_id, limit)



# --- Memory Endpoints ---

@app.get("/api/v1/memory/stats")
async def memory_stats():
    """Get memory system statistics."""

    return memory_store.get_stats()



@app.get("/api/v1/llm/cache-stats")
async def llm_cache_stats():
    """Get LLM cache statistics."""

    from .services.llm import get_llm_service


    llm = get_llm_service()
    return llm.get_cache_stats()


# --- WebSocket for Real-Time Events ---

@app.websocket("/ws/simulation/{sim_id}")
async def simulation_websocket(websocket: WebSocket, sim_id: str):
    """WebSocket endpoint for real-time simulation events."""

    await websocket.accept()

    try:
        while True:
            events = await sim_engine.get_events()
            if events:
                for event in events:
                    await websocket.send_json(event.model_dump())

            await asyncio.sleep(settings.SIMULATION_STREAM_INTERVAL if hasattr(settings, 'SIMULATION_STREAM_INTERVAL') else 0.5)

    except WebSocketDisconnect:
        pass
