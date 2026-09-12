"""Teams API routes."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, verify_api_key
from app.models import Team
from app.schemas.team import TeamCreate, TeamRead
from app.services.audit import log_action

router = APIRouter(prefix="/api/teams", tags=["teams"])

@router.post("", response_model=TeamRead, status_code=status.HTTP_201_CREATED)
def create_team(
    team_in: TeamCreate,
    db: Session = Depends(get_db),
    actor: str = Depends(verify_api_key),
):
    """Create a new team."""
    team = Team(**team_in.model_dump())
    db.add(team)
    db.commit()
    db.refresh(team)

    log_action(db, "team", team.id, "created", actor)
    db.commit()

    return team
