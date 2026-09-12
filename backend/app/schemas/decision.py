"""Pydantic schemas for Decision."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel


class DecisionCreate(BaseModel):
    task_id: UUID
    question: str
    options: list[Any] | None = None


class DecisionResolve(BaseModel):
    selected_option: str
    decided_by: str
    reason: str | None = None


class DecisionRead(BaseModel):
    id: UUID
    task_id: UUID
    question: str
    options: list[Any] | None
    selected_option: str | None
    decided_by: str | None
    reason: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
