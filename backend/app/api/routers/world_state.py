"""World state API routes.

Provides a snapshot of the current situation for the frontend dashboard.
"""

from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, verify_api_key
from app.models import Incident, Location, Resource, Team
from app.schemas.incident import IncidentRead
from app.schemas.location import LocationRead
from app.schemas.resource import ResourceRead
from app.schemas.team import TeamRead

router = APIRouter(prefix="/api/world-state", tags=["world-state"])


@router.get("", response_model=dict[str, Any])
def get_world_state(
    db: Session = Depends(get_db),
    _actor: str = Depends(verify_api_key),
):
    """Returns an aggregate of the current world state."""
    incidents = db.query(Incident).all()
    locations = db.query(Location).all()
    resources = db.query(Resource).all()
    teams = db.query(Team).all()

    return {
        "incidents": [IncidentRead.model_validate(i).model_dump(mode='json') for i in incidents],
        "locations": [LocationRead.model_validate(l).model_dump(mode='json') for l in locations],
        "resources": [ResourceRead.model_validate(r).model_dump(mode='json') for r in resources],
        "teams": [TeamRead.model_validate(t).model_dump(mode='json') for t in teams],
    }
