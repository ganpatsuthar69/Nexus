"""Pydantic schemas for Task."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    plan_id: UUID
    title: str = Field(..., max_length=255)
    description: str | None = None
    status: str = Field(
        "pending",
        pattern=r"^(pending|in_progress|completed|failed|blocked)$",
    )
    priority: int = 0
    assigned_resource_id: UUID | None = None
    assigned_team_id: UUID | None = None
    requires_human: bool = False


class TaskUpdate(BaseModel):
    title: str | None = Field(None, max_length=255)
    description: str | None = None
    status: str | None = Field(
        None,
        pattern=r"^(pending|in_progress|completed|failed|blocked)$",
    )
    priority: int | None = None
    assigned_resource_id: UUID | None = None
    assigned_team_id: UUID | None = None
    requires_human: bool | None = None
    completed_at: datetime | None = None


class TaskRead(BaseModel):
    id: UUID
    plan_id: UUID
    title: str
    description: str | None
    status: str
    priority: int
    assigned_resource_id: UUID | None
    assigned_team_id: UUID | None
    requires_human: bool
    created_at: datetime
    completed_at: datetime | None

    model_config = {"from_attributes": True}
