"""Tests for the resources API."""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import AuditLog


def test_create_and_update_resource(client: TestClient, db: Session):
    # 1. Create Resource
    create_resp = client.post(
        "/api/resources",
        json={
            "name": "Water Tanker 1",
            "resource_type": "water_tanker",
            "status": "available",
            "capacity": 5000,
        },
    )
    assert create_resp.status_code == 201
    resource_id = create_resp.json()["id"]
    
    import uuid
    audit1 = db.query(AuditLog).filter_by(entity_id=uuid.UUID(resource_id)).first()
    assert audit1.action == "created"
    
    # 2. Update Resource
    patch_resp = client.patch(
        f"/api/resources/{resource_id}",
        json={"status": "assigned", "capacity": 4000},
    )
    assert patch_resp.status_code == 200
    data = patch_resp.json()
    assert data["status"] == "assigned"
    assert data["capacity"] == 4000
    
    # Verify update audit log
    audit2 = db.query(AuditLog).filter_by(entity_id=uuid.UUID(resource_id)).order_by(AuditLog.created_at.desc()).first()
    assert audit2.action == "updated"
    assert "status" in audit2.details["updated_fields"]


def test_list_resources(client: TestClient):
    client.post(
        "/api/resources",
        json={"name": "Gen 1", "resource_type": "generator", "status": "available"},
    )
    
    response = client.get("/api/resources")
    assert response.status_code == 200
    assert len(response.json()) == 1
