"""Pydantic schemas for Team."""

from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class TeamCreate(BaseModel):
    name: str = Field(..., max_length=255)
    team_type: str = Field(..., max_length=64)
    status: str = Field(
        "available", pattern=r"^(available|deployed|standby|off_duty)$"
    )
    location_id: UUID | None = None
    capacity: int | None = None
    metadata_: dict[str, Any] | None = Field(None, validation_alias="metadata", serialization_alias="metadata")


class TeamUpdate(BaseModel):
    name: str | None = Field(None, max_length=255)
    team_type: str | None = Field(None, max_length=64)
    status: str | None = Field(
        None, pattern=r"^(available|deployed|standby|off_duty)$"
    )
    location_id: UUID | None = None
    capacity: int | None = None
    metadata_: dict[str, Any] | None = Field(None, validation_alias="metadata", serialization_alias="metadata")


class TeamRead(BaseModel):
    id: UUID
    name: str
    team_type: str
    status: str
    location_id: UUID | None
    capacity: int | None
    metadata_: dict[str, Any] | None = Field(None, validation_alias="metadata_", serialization_alias="metadata")

    model_config = {"from_attributes": True}
