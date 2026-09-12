"""Read-only deterministic tools for Agents."""

import json
from uuid import UUID
from strands import tool

from app.db.session import SessionLocal
from app.models import Incident, Location, Event, Resource, Team
from app.schemas.incident import IncidentRead
from app.schemas.location import LocationRead
from app.schemas.event import EventRead
from app.schemas.resource import ResourceRead
from app.schemas.team import TeamRead


@tool
def get_incident(incident_id: str) -> str:
    """Returns the details of a specific incident as a JSON string."""
    with SessionLocal() as db:
        incident = db.query(Incident).filter(Incident.id == UUID(incident_id)).first()
        if not incident:
            return json.dumps({"error": "Incident not found"})
        return IncidentRead.model_validate(incident).model_dump_json()


@tool
def get_world_state() -> str:
    """Returns a snapshot of the current world state (incidents, locations, resources, teams)."""
    with SessionLocal() as db:
        incidents = [IncidentRead.model_validate(i).model_dump(mode='json') for i in db.query(Incident).all()]
        locations = [LocationRead.model_validate(l).model_dump(mode='json') for l in db.query(Location).all()]
        resources = [ResourceRead.model_validate(r).model_dump(mode='json') for r in db.query(Resource).all()]
        teams = [TeamRead.model_validate(t).model_dump(mode='json') for t in db.query(Team).all()]

        state = {
            "incidents": incidents,
            "locations": locations,
            "resources": resources,
            "teams": teams,
        }
        return json.dumps(state)


@tool
def get_recent_events(incident_id: str, limit: int = 20) -> str:
    """Returns the most recent events related to a specific incident."""
    with SessionLocal() as db:
        events = (
            db.query(Event)
            .filter(Event.incident_id == UUID(incident_id))
            .order_by(Event.created_at.desc())
            .limit(limit)
            .all()
        )
        return json.dumps([EventRead.model_validate(e).model_dump(mode='json') for e in events])


@tool
def find_nearby_resources(location_id: str, resource_type: str = "") -> str:
    """Finds resources located at or near a specific location_id. Optionally filter by resource_type."""
    with SessionLocal() as db:
        query = db.query(Resource).filter(Resource.location_id == UUID(location_id))
        if resource_type:
            query = query.filter(Resource.resource_type == resource_type)
            
        resources = query.all()
        return json.dumps([ResourceRead.model_validate(r).model_dump(mode='json') for r in resources])


@tool
def get_resource_status(resource_id: str) -> str:
    """Returns the current status of a specific resource."""
    with SessionLocal() as db:
        resource = db.query(Resource).filter(Resource.id == UUID(resource_id)).first()
        if not resource:
            return json.dumps({"error": "Resource not found"})
        return ResourceRead.model_validate(resource).model_dump_json()


@tool
def get_available_teams(team_type: str, location_id: str = "") -> str:
    """Returns a list of teams of a specific type that are currently 'available'."""
    with SessionLocal() as db:
        query = db.query(Team).filter(Team.team_type == team_type, Team.status == "available")
        if location_id:
            query = query.filter(Team.location_id == UUID(location_id))
            
        teams = query.all()
        return json.dumps([TeamRead.model_validate(t).model_dump(mode='json') for t in teams])
