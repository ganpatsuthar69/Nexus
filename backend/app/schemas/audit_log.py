"""Pydantic schemas for AuditLog."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class AuditLogCreate(BaseModel):
    entity_type: str = Field(..., max_length=64)
    entity_id: UUID
    action: str = Field(..., max_length=64)
    actor: str = Field(..., max_length=128)
    details: dict[str, Any] | None = None


class AuditLogRead(BaseModel):
    id: UUID
    entity_type: str
    entity_id: UUID
    action: str
    actor: str
    details: dict[str, Any] | None
    created_at: datetime

    model_config = {"from_attributes": True}
