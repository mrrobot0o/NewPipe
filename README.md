# Teresa - Next-Gen Swarm Intelligence Engine

[![Teresa Logo](https://img.shields.io/badge/Teresa-Swarm%20Intelligence-blue)](https://github.com/HMida/teresa)
[![Version](https://img.shields.io/badge/v0.1.0-DAY2-yellow)](https://github.com/HMida/teresa)
[![Python](https://img.shields.io/badge/Python-3.11+-green)](https://python.org)
[![Next.js](https://img.shields.io/badge/Next.js-15-red)](https://nextjs.org)

🚀 **Teresa** is a next-generation swarm intelligence prediction engine, significantly more powerful than MiroFish. Built with multi-agent technology, personality systems, and real-time collaboration.

---

## ✨ What is Teresa?

Teresa creates a high-fidelity parallel digital world where thousands of intelligent agents with independent personalities, long-term memory, and behavioral logic interact and evolve. By injecting variables from a "God's-eye view," you can precisely deduce future trajectories.

**Core Capabilities:**
- **10,000+ Agents** - Scalable swarm intelligence
- **8 Personality Types** - Analyst, Optimist, Skeptic, Innovator, Pragmatist, Critic, Diplomat, Visionary
- **3-Tier Memory System** - Working, Episodic, and Semantic memory
- **Real-time Chat** - LLM-powered conversations with agents
- **Network Visualization** - Live agent interaction graphs
- **Prediction Reports** - AI-generated insights and recommendations

---

## 📋 Development Progress (10 Days)

### ✅ Day 1 (Apr 10) - Core Infrastructure
- [x] Backend: FastAPI structure, models, configuration
- [x] Agent Engine: 8 roles, Big Five personality model
- [x] Memory System: Working, Episodic, Semantic memory
- [x] Simulation Engine: Parallel interactions, consensus building
- [x] API: REST endpoints, WebSocket streaming
- [x] Frontend: Next.js dashboard with visualization

### ✅ Day 2 (Apr 10) - LLM Integration
- [x] **LLM Service** - OpenAI-compatible API with caching
- [x] **Agent Chat Service** - Real-time conversations with agents
- [x] **Personality-Aware Prompts** - Agents respond according to personality
- [x] **New API Endpoints** - Chat, batch chat, debates, history
- [x] **Frontend Chat UI** - Modal-based chat interface
- [x] **Agent List** - Click to chat with any agent

### 🚧 Day 3 (Apr 11) - Seed Data Processing (Next)
- [ ] Multi-modal seed parsing (text, images, PDFs)
- [ ] Entity extraction from seeds
- [ ] Knowledge graph construction
- [ ] Seed upload UI
- [ ] Real-time seed processing status

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│              Frontend (Next.js 15)              │
│   Dashboard | Chat | Visualization | Analytics   │
└──────────────┬───────────────────────────────┘
               │ WebSocket
               │
┌──────────────▼───────────────────────────────┐
│           API Gateway (FastAPI)                │
│      REST | WebSocket | Chat | Simulation     │
└──────────────┬───────────────────────────────┘
               │
       ┌───────┴────────┬──────────┬────────┐
       │                │          │        │
┌──────▼────┐   ┌──────▼────┐ ┌──▼───────▼───┐
│  Agent    │   │  Memory   │ │ Simulation   │
│  Engine   │   │  Store    │ │  Engine      │
└───────────┘   └──────────┘ └─────────────┘
                │                │
       ┌───────▼────┐   ┌───────▼────┐
       │Vector DB   │   │   LLM      │
       │(Qdrant)    │   │  Service   │
       └────────────┘   └────────────┘
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Git

### 1. Clone Repository
```bash
git clone https://github.com/HMida/teresa.git
cd teresa
```

### 2. Backend Setup
```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your LLM API key (OpenAI, Anthropic, etc.)

# Start backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env.local
# Edit .env.local with backend URL

# Start frontend
npm run dev
```

### 4. Open Browser
Visit `http://localhost:3000` to access the Teresa dashboard.

---

## 🔧 Configuration

### Environment Variables

#### Backend (`.env`)
```env
# LLM Configuration (OpenAI-compatible)
LLM_API_KEY=your_api_key_here
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL_NAME=gpt-4o
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=4096

# Agent defaults
MAX_AGENTS=10000
AGENT_INTERACTION_ROUNDS=40

# Memory
MEMORY_BACKEND=qdrant
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION=teresa_memory

# Database
DATABASE_URL=postgresql://teresa:teresa@localhost:5432/teresa
```

#### Frontend (`.env.local`)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 🧩 Core Features

### Multi-Agent System
- **8 Personalities**: Each agent has Big Five personality traits
- **Memory Architecture**: Working + Episodic + Semantic memory
- **Social Networks**: Agents form relationships and influence each other
- **Evolution**: Agents learn and adapt from interactions

### Intelligent Chat
- **Personality-Aware Responses**: Agents respond according to their roles
- **Batch Chat**: Send message to multiple agents simultaneously
- **Debates**: Simulate arguments between opposing personality types
- **History**: Conversation tracking with contextual awareness

### Real-time Simulation
- **WebSocket Streaming**: Live updates on agent interactions
- **Consensus Building**: Agents work toward collective predictions
- **Visualization**: Network graphs and interaction heatmaps
- **Progress Tracking**: Real-time metrics and evolution

---

## 📁 Project Structure

```
teresa/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── agents/            # Agent engine and behavior
│   │   ├── core/             # Configuration and utilities
│   │   ├── models/           # Data models (Agent, Simulation)
│   │   ├── services/         # LLM service, chat service
│   │   ├── memory/           # Memory system
│   │   ├── simulation/       # Simulation engine
│   │   └── main.py           # FastAPI application
│   ├── requirements.txt      # Python dependencies
│   └── .env.example         # Environment template
│
├── frontend/                  # Next.js 15 frontend
│   ├── src/
│   │   ├── app/             # Next.js app router
│   │   └── components/     # React components
│   ├── package.json         # Node.js dependencies
│   └── tailwind.config.js   # Tailwind CSS
│
├── PROGRESS.md              # 10-day development plan
└── README.md               # This file
```

---

## 🔗 API Endpoints

### Simulation
- `POST /api/v1/simulations` - Create new simulation
- `POST /api/v1/simulations/{id}/run` - Start simulation
- `GET /api/v1/simulations/{id}` - Get simulation details
- `POST /api/v1/simulations/{id}/stop` - Stop simulation

### Agents
- `GET /api/v1/agents` - List all agents
- `GET /api/v1/agents/{id}` - Get agent details
- `POST /api/v1/agents/{id}/chat` - Chat with agent (LLM)
- `POST /api/v1/agents/batch-chat` - Send to multiple agents
- `POST /api/v1/agents/debate` - Simulate debate
- `GET /api/v1/agents/{id}/history` - Get conversation history

### Memory
- `GET /api/v1/memory/stats` - Memory statistics
- `GET /api/v1/llm/cache-stats` - LLM cache statistics

### WebSocket
- `ws://localhost:8000/ws/simulation/{id}` - Real-time events

---

## 🧪 Features Demonstrated

### 1. Agent Personality System
```python
# Agents have distinct personalities based on Big Five model
personality = {
    "openness": 0.7,        # Creative, curious
    "conscientiousness": 0.9,  # Organized, methodical  
    "extraversion": 0.3,    # Reserved, private
    "agreeableness": 0.5,   # Neutral to conflict
    "neuroticism": 0.3      # Stable, low anxiety
}
```

### 2. LLM Integration
```python
# Personality-aware prompt system
response = await llm.generate_agent_response(
    agent_name="Ada Chen",
    agent_role="analyst",
    personality=personality,
    context=memory_context,
    user_message="What do you think about this trend?"
)
```

### 3. Real-time Chat
- Click any agent to start a conversation
- Agents respond with their unique personality
- Conversation history preserved
- Multiple conversation modes (chat, debate, batch)

---

## 📊 Comparison: Teresa vs MiroFish

| Feature | MiroFish | Teresa |
|---------|-----------|---------|
| Max Agents | ~1,000 | **10,000** |
| Personality Model | Basic | **Big Five + 8 Roles** |
| Memory System | Simple | **3-Tier (Working/Episodic/Semantic)** |
| Real-time Features | Limited | **WebSocket + Live Visualization** |
| Chat Interface | None | **LLM-Powered Agent Chat** |
| Caching | None | **Intelligent LLM Cache** |
| Development Status | Existing | **Active Development** |

---

## 🛠️ Technologies Used

### Backend
- **FastAPI** - High-performance web framework
- **Python 3.11+** - Core language
- **Pydantic** - Data validation
- **OpenAI** - LLM API integration
- **AsyncIO** - Concurrent processing
- **WebSocket** - Real-time communication

### Frontend
- **Next.js 15** - React framework with app router
- **Tailwind CSS** - Utility-first styling
- **TypeScript** - Type safety
- **React Hooks** - State management
- **Framer Motion** - Animations
- **Lucide React** - Icon library

### AI/ML
- **OpenAI API** - LLM integration
- **Custom Prompts** - Personality-aware responses
- **Vector Memory** - Semantic storage (future Qdrant)
- **Multi-Agent Systems** - Swarm intelligence

---

## 🎯 Use Cases

### Business Strategy
- Predict market trends with 10,000+ perspectives
- Test policies in risk-free digital environment
- Optimize decision-making with agent consensus

### Creative Writing
- Generate novel endings with 8 personality types
- Explore "what-if" scenarios interactively
- Character development through agent interactions

### Research
- Social science simulations
- Predictive analytics
- Collective decision-making modeling

### Education
- Interactive learning through agent dialogue
- Understanding diverse perspectives
- Debating complex topics

---

## 🤝 Contributing

This is an active 10-day development project. The project follows a structured 10-day roadmap (see PROGRESS.md).

To contribute:
1. Check the current day's tasks in PROGRESS.md
2. Fork the repository
3. Create a feature branch
4. Commit your changes
5. Push to your fork and submit a pull request

---

## 📄 License

MIT License - see LICENSE file for details.

---

## 🚀 Development Roadmap

- [ ] Day 3: Seed Data Processing (Images, PDFs, Multi-modal)
- [ ] Day 4: Advanced Memory with Vector Embeddings
- [ ] Day 5: Analytics Engine with Heatmaps
- [ ] Day 6: Real-time Enhancements & 3D Visualization
- [ ] Day 7: Report Generation & Export
- [ ] Day 8: Production Features (Auth, History)
- [ ] Day 9: Testing & Performance Optimization
- [ ] Day 10: Deployment & Demo

---

## 📞 Contact

- **Project Lead**: HMida
- **GitHub**: [HMida/teresa](https://github.com/HMida/teresa)
- **Status**: Active Development (10-day sprint)

---

**Teresa** - Predicting the future through collective intelligence. 🌟