"""Locations API routes."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, verify_api_key
from app.models import Location
from app.schemas.location import LocationCreate, LocationRead
from app.services.audit import log_action

router = APIRouter(prefix="/api/locations", tags=["locations"])

@router.post("", response_model=LocationRead, status_code=status.HTTP_201_CREATED)
def create_location(
    location_in: LocationCreate,
    db: Session = Depends(get_db),
    actor: str = Depends(verify_api_key),
):
    """Create a new location."""
    location = Location(**location_in.model_dump())
    db.add(location)
    db.commit()
    db.refresh(location)

    log_action(db, "location", location.id, "created", actor)
    db.commit()

    return location
