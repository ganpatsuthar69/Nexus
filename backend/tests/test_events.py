"""Tests for the events API and deduplication."""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import AuditLog


def test_create_event_and_dedup(client: TestClient, db: Session):
    event_payload = {
        "event_type": "report",
        "source": "citizen_app",
        "description": "Fire in the building",
        "severity": "high",
        "confidence": 0.8,
    }
    
    # 1. Create event
    response1 = client.post("/api/events", json=event_payload)
    assert response1.status_code == 201
    data1 = response1.json()
    assert data1["source"] == "citizen_app"
    assert data1["dedup_key"] is not None
    
    # Verify audit log
    audits = db.query(AuditLog).filter_by(entity_type="event").all()
    assert len(audits) == 1
    
    # 2. Submit exact same event (deduplication check)
    response2 = client.post("/api/events", json=event_payload)
    # The API is idempotent and returns 201 with the existing event
    assert response2.status_code == 201
    data2 = response2.json()
    
    # The IDs should match exactly (no new row created)
    assert data1["id"] == data2["id"]
    
    # Verify NO new audit log was created for the duplicate request
    audits_after = db.query(AuditLog).filter_by(entity_type="event").all()
    assert len(audits_after) == 1


def test_list_events(client: TestClient):
    client.post(
        "/api/events",
        json={"event_type": "sensor", "source": "iot_1", "severity": "low"},
    )
    
    response = client.get("/api/events")
    assert response.status_code == 200
    assert len(response.json()) == 1
