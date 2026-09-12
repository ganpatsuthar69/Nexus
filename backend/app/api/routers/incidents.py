"""Incident API routes."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, verify_api_key
from app.models import Incident, Plan
from app.schemas.incident import IncidentCreate, IncidentRead
from app.schemas.plan import PlanRead
from app.services.audit import log_action

router = APIRouter(prefix="/api/incidents", tags=["incidents"])


@router.post("", response_model=IncidentRead, status_code=status.HTTP_201_CREATED)
def create_incident(
    incident_in: IncidentCreate,
    db: Session = Depends(get_db),
    actor: str = Depends(verify_api_key),
):
    """Create a new incident and record an audit log."""
    incident = Incident(**incident_in.model_dump())
    db.add(incident)
    db.commit()
    db.refresh(incident)

    log_action(db, "incident", incident.id, "created", actor)
    db.commit()

    return incident


@router.get("", response_model=list[IncidentRead])
def list_incidents(
    db: Session = Depends(get_db),
    _actor: str = Depends(verify_api_key),
):
    """List all incidents."""
    return db.query(Incident).all()


@router.get("/{incident_id}", response_model=IncidentRead)
def get_incident(
    incident_id: UUID,
    db: Session = Depends(get_db),
    _actor: str = Depends(verify_api_key),
):
    """Get a specific incident by ID."""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


@router.get("/{incident_id}/plans", response_model=list[PlanRead])
def get_incident_plans(
    incident_id: UUID,
    db: Session = Depends(get_db),
    _actor: str = Depends(verify_api_key),
):
    """Get all plans for a specific incident."""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    return db.query(Plan).filter(Plan.incident_id == incident_id).all()
