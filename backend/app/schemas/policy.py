"""Pydantic schemas for Policy."""

from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class PolicyCreate(BaseModel):
    action_type: str = Field(..., max_length=64)
    max_impact_scope: str | None = Field(None, max_length=64)
    requires_human: bool = False
    auto_approve_conditions: dict[str, Any] | None = None


class PolicyUpdate(BaseModel):
    max_impact_scope: str | None = Field(None, max_length=64)
    requires_human: bool | None = None
    auto_approve_conditions: dict[str, Any] | None = None


class PolicyRead(BaseModel):
    id: UUID
    action_type: str
    max_impact_scope: str | None
    requires_human: bool
    auto_approve_conditions: dict[str, Any] | None

    model_config = {"from_attributes": True}
