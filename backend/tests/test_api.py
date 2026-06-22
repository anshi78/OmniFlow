"""Integrative tests for FastAPI REST routers."""

import pytest

@pytest.mark.asyncio
async def test_health_check(client):
    """Test health check route returns healthy status."""
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

@pytest.mark.asyncio
async def test_root_route(client):
    """Test root endpoint returns application metadata."""
    response = await client.get("/")
    assert response.status_code == 200
    assert response.json()["name"] == "OmniFlow AI"

@pytest.mark.asyncio
async def test_agents_graph_route(client):
    """Test retrieving agent visualization nodes/edges."""
    response = await client.get("/api/agents/graph")
    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data
    assert "edges" in data
    assert len(data["nodes"]) > 0

@pytest.mark.asyncio
async def test_run_agents_pipeline(client):
    """Test POST trigger of the multi-agent system."""
    payload = {"query": "Check stock levels for category Electronics"}
    response = await client.post("/api/agents/run", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert "decisions_count" in data
    assert "messages" in data
