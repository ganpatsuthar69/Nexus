"""Pydantic schemas for Incident."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class IncidentCreate(BaseModel):
    title: str = Field(..., max_length=255)
    description: str | None = None
    status: str = Field("open", pattern=r"^(open|in_progress|resolved|closed)$")
    severity: str = Field("medium", pattern=r"^(low|medium|high|critical)$")


class IncidentUpdate(BaseModel):
    title: str | None = Field(None, max_length=255)
    description: str | None = None
    status: str | None = Field(None, pattern=r"^(open|in_progress|resolved|closed)$")
    severity: str | None = Field(None, pattern=r"^(low|medium|high|critical)$")


class IncidentRead(BaseModel):
    id: UUID
    title: str
    description: str | None
    status: str
    severity: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
