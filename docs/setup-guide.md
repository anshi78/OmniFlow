# 🚀 OmniFlow AI — Setup and Running Guide

This guide will walk you through setting up and running **OmniFlow AI** locally and using Docker.

---

## 💻 Local Quickstart (Development Mode)

The project is pre-configured with **SQLite** and **in-memory fallbacks** for Redis, Kafka, and OpenAI, so you can run the entire system without running external servers.

### 1. Prerequisites
- **Python 3.11+**
- **Node.js 20+** and **npm**

### 2. Backend Setup
1. Open a terminal and navigate to the backend folder:
   ```bash
   cd backend
   ```
2. Create a virtual environment and activate it:
   ```bash
   python -m venv .venv
   # Windows:
   .\.venv\Scripts\activate
   # macOS/Linux:
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -e '.[dev]'
   ```
4. Run the FastAPI development server:
   ```bash
   uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```
   * The database will automatically initialize as a SQLite file `omniflow.db` and generate realistic product and inventory seed data!
   * The API docs will be available at `http://127.0.0.1:8000/docs`.

### 3. Frontend Setup
1. Open a new terminal and navigate to the frontend folder:
   ```bash
   cd frontend
   ```
2. Install npm packages:
   ```bash
   npm install
   ```
3. Run the Next.js development server:
   ```bash
   npm run dev
   ```
4. Open your browser and navigate to `http://localhost:3000`.

---

## 🐳 Running with Docker (Production Grade)

To run the complete production-grade system with **PostgreSQL (with pgvector)**, **Redis (Digital Twin cache)**, and **Apache Kafka (Event Bus)**, use Docker Compose.

1. Ensure **Docker Desktop** is running.
2. Run the compose build:
   ```bash
   docker compose up --build
   ```
3. Docker will build both Next.js and FastAPI services and link them with postgres, redis, and kafka containers.
4. Access the frontend dashboard at `http://localhost:3000`.
