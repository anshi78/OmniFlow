# 🌊 OmniFlow AI

### Multi-Agent Retail Inventory Optimization System

> AI-powered Digital Twin for Supply Chain Intelligence

![Architecture](https://img.shields.io/badge/Architecture-Multi--Agent-blue)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688)
![Next.js](https://img.shields.io/badge/Frontend-Next.js%2015-black)
![LangGraph](https://img.shields.io/badge/AI-LangGraph-purple)
![PostgreSQL](https://img.shields.io/badge/DB-PostgreSQL-336791)

---

## 🚀 What is OmniFlow AI?

OmniFlow AI is a **production-quality** multi-agent system that optimizes retail inventory management by:

- 📊 **Forecasting demand** with XGBoost ML models
- 🏪 **Monitoring inventory** across stores and warehouses in real-time
- ⚡ **Detecting disruptions** (supplier delays, weather events, viral trends)
- 🏭 **Coordinating warehouses** for optimal stock allocation
- 🗺️ **Optimizing logistics** with route planning and carbon scoring
- 🤖 **Autonomous decision-making** via LangGraph agent orchestration
- 🔮 **Simulating supply-chain events** with Digital Twin technology

---

## 🏗️ Architecture

```
Frontend (Next.js 15 + ShadCN UI)
        ↓
  FastAPI Gateway (REST + WebSocket)
        ↓
  LangGraph Agent Layer
  ├── Orchestrator Agent
  ├── Demand Forecast Agent
  ├── Store Agent
  ├── Warehouse Agent
  ├── Supplier Agent
  ├── Logistics Agent
  ├── Trend Agent
  └── Inventory Optimizer Agent
        ↓
  Redis (Digital Twin + Cache)
        ↓
  PostgreSQL + pgvector (Data + Vector Memory)
        ↓
  Kafka Event Bus
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 15, TypeScript, Tailwind CSS, ShadCN UI, Recharts, Framer Motion |
| Backend | FastAPI, Python 3.11+, SQLAlchemy, Pydantic |
| AI/ML | LangGraph, LangChain, OpenAI, XGBoost |
| Database | PostgreSQL + pgvector, SQLite (dev) |
| Cache | Redis |
| Events | Apache Kafka |
| Deploy | Docker, Kubernetes, GitHub Actions |

---

## 📦 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- (Optional) Docker & Docker Compose

### 1. Clone & Setup

```bash
git clone https://github.com/your-org/omniflow-ai.git
cd omniflow-ai
cp .env.example .env
```

### 2. Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

### 4. Access

- 🖥️ Dashboard: http://localhost:3000
- 📡 API Docs: http://localhost:8000/docs
- 🔄 WebSocket: ws://localhost:8000/ws

### Docker (Full Stack)

```bash
docker compose up --build
```

---

## 🔑 Default Credentials

| Email | Password | Role |
|-------|----------|------|
| admin@omniflow.ai | admin123 | Admin |
| manager@omniflow.ai | manager123 | Manager |

---

## 📊 Features

### Dashboard
- Real-time inventory stats with animated counters
- Demand forecast charts with confidence bands
- Risk heatmap by region
- Live agent activity feed

### Simulation Center
- 5 scenario types (Demand Spike, Supplier Strike, Weather, etc.)
- Multi-dimensional impact analysis
- Agent decision replay

### Agent Monitoring
- Communication graph visualization
- Event timeline with filtering
- Reasoning transparency ("Why did AI decide this?")

### Explainable AI
- Every recommendation includes: `{reason, confidence_score, factors_used}`
- Root cause analysis
- Decision audit trail

---

## 📄 License

MIT © 2025 OmniFlow AI Team
