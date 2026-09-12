"""Integration tests for the Agent API routes."""

import pytest
from fastapi.testclient import TestClient
from uuid import uuid4

from app.main import app
from app.models import Incident, Event

# We will patch the orchestrator so we don't actually trigger Bedrock calls in tests
from unittest.mock import patch

@patch("app.api.routers.agent.Orchestrator")
def test_run_agent(MockOrchestrator, client, db):
    # Setup incident
    incident_id = uuid4()
    inc = Incident(id=incident_id, title="Test", description="Test", status="active", severity="low")
    db.add(inc)
    db.commit()

    response = client.post(f"/api/agent/run?incident_id={str(incident_id)}")
    assert response.status_code == 200
    assert response.json()["status"] == "accepted"


@patch("app.api.routers.agent.Orchestrator")
def test_ingest_agent_event(MockOrchestrator, client, db):
    incident_id = uuid4()
    inc = Incident(id=incident_id, title="Test", description="Test", status="active", severity="low")
    db.add(inc)
    db.commit()

    event_payload = {
        "incident_id": str(incident_id),
        "event_type": "observation",
        "source": "citizen",
        "description": "Fire spotted",
        "severity": "high"
    }

    response = client.post("/api/agent/events", json=event_payload)
    assert response.status_code == 200
    assert response.json()["status"] == "accepted"
    
    # Test dedup
    response2 = client.post("/api/agent/events", json=event_payload)
    assert response2.status_code == 200
    assert response2.json()["status"] == "duplicate"
