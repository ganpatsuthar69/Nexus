"""Pydantic schemas for Resource."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class ResourceCreate(BaseModel):
    name: str = Field(..., max_length=255)
    resource_type: str = Field(..., max_length=64)
    status: str = Field(
        "available",
        pattern=r"^(available|assigned|in_transit|depleted|maintenance)$",
    )
    capacity: int | None = None
    location_id: UUID | None = None
    metadata_: dict[str, Any] | None = Field(None, validation_alias="metadata", serialization_alias="metadata")


class ResourceUpdate(BaseModel):
    name: str | None = Field(None, max_length=255)
    resource_type: str | None = Field(None, max_length=64)
    status: str | None = Field(
        None,
        pattern=r"^(available|assigned|in_transit|depleted|maintenance)$",
    )
    capacity: int | None = None
    location_id: UUID | None = None
    metadata_: dict[str, Any] | None = Field(None, validation_alias="metadata", serialization_alias="metadata")


class ResourceRead(BaseModel):
    id: UUID
    name: str
    resource_type: str
    status: str
    capacity: int | None
    location_id: UUID | None
    metadata_: dict[str, Any] | None = Field(None, validation_alias="metadata_", serialization_alias="metadata")
    updated_at: datetime

    model_config = {"from_attributes": True}
