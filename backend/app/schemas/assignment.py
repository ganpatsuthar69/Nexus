"""Pydantic schemas for Assignment."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class AssignmentCreate(BaseModel):
    resource_id: UUID | None = None
    team_id: UUID | None = None
    task_id: UUID | None = None
    status: str = Field(
        "pending", pattern=r"^(pending|active|completed|cancelled)$"
    )


class AssignmentUpdate(BaseModel):
    status: str | None = Field(
        None, pattern=r"^(pending|active|completed|cancelled)$"
    )
    completed_at: datetime | None = None


class AssignmentRead(BaseModel):
    id: UUID
    resource_id: UUID | None
    team_id: UUID | None
    task_id: UUID | None
    status: str
    assigned_at: datetime
    completed_at: datetime | None

    model_config = {"from_attributes": True}
