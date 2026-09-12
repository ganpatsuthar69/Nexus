"""Decisions API routes."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, verify_api_key
from app.models import Decision
from app.schemas.decision import DecisionRead, DecisionResolve
from app.services.audit import log_action

router = APIRouter(prefix="/api/decisions", tags=["decisions"])


@router.get("/pending", response_model=list[DecisionRead])
def list_pending_decisions(
    db: Session = Depends(get_db),
    _actor: str = Depends(verify_api_key),
):
    """List decisions that are awaiting a human response."""
    return db.query(Decision).filter(Decision.selected_option.is_(None)).all()


@router.post("/{decision_id}/resolve", response_model=DecisionRead)
def resolve_decision(
    decision_id: UUID,
    resolution: DecisionResolve,
    db: Session = Depends(get_db),
    actor: str = Depends(verify_api_key),
):
    """Resolve a pending decision with a selected option."""
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")
    if decision.selected_option is not None:
        raise HTTPException(status_code=400, detail="Decision is already resolved")

    decision.selected_option = resolution.selected_option
    decision.decided_by = resolution.decided_by
    decision.reason = resolution.reason

    db.add(decision)
    db.commit()
    db.refresh(decision)

    log_action(
        db=db,
        entity_type="decision",
        entity_id=decision.id,
        action="resolved",
        actor=actor,
        details={"selected_option": resolution.selected_option},
    )
    db.commit()

    return decision
