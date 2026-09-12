"""Tests for deterministic Agent tools."""

import json
from uuid import uuid4
from sqlalchemy.orm import Session

from app.models import Event, Task, Resource, Plan
from app.tools.actions import verify_event, assign_resource


import pytest
from unittest.mock import patch

@pytest.fixture(autouse=True)
def mock_session_local(db):
    """Patch SessionLocal in actions module to return the test db session.
    We yield the db session when it's used as a context manager.
    """
    class MockSessionManager:
        def __enter__(self):
            return db
        def __exit__(self, *args):
            pass

    with patch('app.tools.actions.SessionLocal', return_value=MockSessionManager()):
        yield

def test_verify_event_confidence_scoring(db: Session):
    # Setup test event
    event = Event(
        id=uuid4(),
        event_type="test",
        source="citizen",
        severity="low",
        confidence=0.0
    )
    db.add(event)
    db.commit()

    # Test auto-accept (>0.8)
    res_str = verify_event(
        event_id=str(event.id),
        source_trust_weight=0.5,
        corroboration_count_weight=0.4,
        recency_weight=0.1,
        contradiction_penalty=0.0
    )
    res = json.loads(res_str)
    assert "error" not in res, f"Error returned: {res}"
    assert res["confidence"] == 1.0
    assert res["status"] == "auto_accepted"

    # Test flag (0.4-0.8)
    res_str = verify_event(
        event_id=str(event.id),
        source_trust_weight=0.3,
        corroboration_count_weight=0.2,
        recency_weight=0.1,
        contradiction_penalty=0.0
    )
    res = json.loads(res_str)
    assert res["confidence"] == 0.6
    assert res["status"] == "flagged_for_verification"

    # Test hold (<0.4)
    res_str = verify_event(
        event_id=str(event.id),
        source_trust_weight=0.1,
        corroboration_count_weight=0.1,
        recency_weight=0.1,
        contradiction_penalty=0.0
    )
    res = json.loads(res_str)
    assert round(res["confidence"], 1) == 0.3
    assert res["status"] == "held"


def test_assign_resource_idempotency(db: Session):
    # Setup plan, task, resource
    plan = Plan(id=uuid4(), incident_id=uuid4(), goal="test", status="draft", version=1)
    task = Task(id=uuid4(), plan_id=plan.id, title="Test Task", status="pending", priority=1)
    resource = Resource(id=uuid4(), name="Test Res", resource_type="truck", status="available")
    
    db.add_all([plan, task, resource])
    db.commit()

    # First assignment should succeed
    res_str = assign_resource(task_id=str(task.id), resource_id=str(resource.id))
    res = json.loads(res_str)
    assert "error" not in res, f"Error returned: {res}"
    assert res["status"] == "success"

    # Second assignment with same task and resource should return already_assigned
    res_str2 = assign_resource(task_id=str(task.id), resource_id=str(resource.id))
    res2 = json.loads(res_str2)
    assert res2["status"] == "already_assigned"

    # Try assigning to a different task
    task2 = Task(id=uuid4(), plan_id=plan.id, title="Test Task 2", status="pending", priority=1)
    db.add(task2)
    db.commit()

    res_str3 = assign_resource(task_id=str(task2.id), resource_id=str(resource.id))
    res3 = json.loads(res_str3)
    assert "error" in res3
    assert "already assigned" in res3["error"]
