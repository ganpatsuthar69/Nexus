"""Pydantic schemas for Event."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class EventCreate(BaseModel):
    incident_id: UUID | None = None
    event_type: str = Field(..., max_length=64)
    source: str = Field(..., max_length=128)
    description: str | None = None
    location_id: UUID | None = None
    severity: str = Field("medium", pattern=r"^(low|medium|high|critical)$")
    confidence: float = Field(1.0, ge=0.0, le=1.0)
    dedup_key: str | None = Field(None, max_length=128)


class EventRead(BaseModel):
    id: UUID
    incident_id: UUID | None
    event_type: str
    source: str
    description: str | None
    location_id: UUID | None
    severity: str
    confidence: float
    created_at: datetime
    processed_at: datetime | None
    dedup_key: str | None

    model_config = {"from_attributes": True}
