"""Pydantic schemas for Plan."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class PlanCreate(BaseModel):
    incident_id: UUID
    goal: str
    status: str = Field(
        "draft", pattern=r"^(draft|active|completed|failed|superseded)$"
    )
    version: int = 1
    reason: str | None = None
    approved_by: str | None = None


class PlanUpdate(BaseModel):
    goal: str | None = None
    status: str | None = Field(
        None, pattern=r"^(draft|active|completed|failed|superseded)$"
    )
    version: int | None = None
    reason: str | None = None
    approved_by: str | None = None


from .task import TaskRead

class PlanRead(BaseModel):
    id: UUID
    incident_id: UUID
    goal: str
    status: str
    version: int
    reason: str | None
    created_at: datetime
    approved_by: str | None
    tasks: list[TaskRead] = []

    model_config = {"from_attributes": True}
