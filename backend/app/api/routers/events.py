"""Events API routes."""

import hashlib
from typing import Any

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, verify_api_key
from app.models import Event
from app.schemas.event import EventCreate, EventRead
from app.services.audit import log_action

router = APIRouter(prefix="/api/events", tags=["events"])


def compute_dedup_key(event_in: EventCreate) -> str:
    """Computes a stable hash based on source, location, and description.
    
    In a real system this might also include a time bucket.
    """
    if event_in.dedup_key:
        return event_in.dedup_key
        
    components = [
        event_in.source,
        str(event_in.location_id) if event_in.location_id else "none",
        event_in.description or "none",
    ]
    key_str = "|".join(components)
    return hashlib.sha256(key_str.encode("utf-8")).hexdigest()


@router.post("", response_model=EventRead, status_code=status.HTTP_201_CREATED)
def create_event(
    event_in: EventCreate,
    db: Session = Depends(get_db),
    actor: str = Depends(verify_api_key),
):
    """Create a new event with deduplication check."""
    dedup_key = compute_dedup_key(event_in)
    
    # Check for existing event
    existing_event = db.query(Event).filter(Event.dedup_key == dedup_key).first()
    if existing_event:
        # Idempotent return — return the existing event with 200 OK
        # We can change the response status to 200 by returning the existing
        # one, but FastAPI's default for this route is 201. For idempotency,
        # it is often acceptable to return 201 or we could explicitly set response code.
        return existing_event

    # Create new event
    event_data = event_in.model_dump()
    event_data["dedup_key"] = dedup_key
    
    event = Event(**event_data)
    db.add(event)
    db.commit()
    db.refresh(event)

    log_action(db, "event", event.id, "created", actor)
    db.commit()

    return event


@router.get("", response_model=list[EventRead])
def list_events(
    db: Session = Depends(get_db),
    _actor: str = Depends(verify_api_key),
):
    """List all events."""
    return db.query(Event).all()
