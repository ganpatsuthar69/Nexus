"""Tests for the incidents API."""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import AuditLog


def test_create_incident(client: TestClient, db: Session):
    response = client.post(
        "/api/incidents",
        json={
            "title": "Test Incident",
            "description": "A test incident",
            "status": "open",
            "severity": "high",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Incident"
    assert "id" in data
    
    # Verify audit log was created
    audit = db.query(AuditLog).filter_by(entity_type="incident").first()
    assert audit is not None
    assert audit.action == "created"
    assert str(audit.entity_id) == data["id"]


def test_list_incidents(client: TestClient):
    # Create one first
    client.post(
        "/api/incidents",
        json={"title": "Test 1", "status": "open", "severity": "low"},
    )
    
    response = client.get("/api/incidents")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Test 1"


def test_get_incident(client: TestClient):
    create_resp = client.post(
        "/api/incidents",
        json={"title": "Test 2", "status": "open", "severity": "low"},
    )
    incident_id = create_resp.json()["id"]
    
    response = client.get(f"/api/incidents/{incident_id}")
    assert response.status_code == 200
    assert response.json()["id"] == incident_id


def test_auth_required(client: TestClient):
    # Remove the API key
    del client.headers["X-API-Key"]
    response = client.get("/api/incidents")
    assert response.status_code == 401
