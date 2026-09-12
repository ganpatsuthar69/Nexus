"""Pydantic schemas for Location."""

from uuid import UUID

from pydantic import BaseModel, Field


class LocationCreate(BaseModel):
    name: str = Field(..., max_length=255)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    population: int | None = None
    priority: int = 0
    current_status: str = Field(
        "normal", pattern=r"^(normal|affected|evacuated|sheltering)$"
    )


class LocationUpdate(BaseModel):
    name: str | None = Field(None, max_length=255)
    latitude: float | None = Field(None, ge=-90, le=90)
    longitude: float | None = Field(None, ge=-180, le=180)
    population: int | None = None
    priority: int | None = None
    current_status: str | None = Field(
        None, pattern=r"^(normal|affected|evacuated|sheltering)$"
    )


class LocationRead(BaseModel):
    id: UUID
    name: str
    latitude: float
    longitude: float
    population: int | None
    priority: int
    current_status: str

    model_config = {"from_attributes": True}
