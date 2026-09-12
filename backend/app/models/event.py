"""Event model — incoming report or signal about the world.

Includes a dedup_key column with a unique index to prevent duplicate
event ingestion (source + location + description_hash + time_bucket).
"""

import uuid
from datetime import datetime

from sqlalchemy import String, Text, Float, DateTime, ForeignKey, Index, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Event(Base):
    __tablename__ = "events"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    incident_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("incidents.id"), nullable=True
    )
    event_type: Mapped[str] = mapped_column(
        String(64), nullable=False,
        comment="report | sensor | update | alert | resolution",
    )
    source: Mapped[str] = mapped_column(
        String(128), nullable=False,
        comment="Origin of the event: citizen_report, iot_sensor, official_update, …",
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    location_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("locations.id"), nullable=True
    )
    severity: Mapped[str] = mapped_column(
        String(16), nullable=False, default="medium",
        comment="low | medium | high | critical",
    )
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    processed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # ── Dedup key ────────────────────────────────────────────────────
    # Composite hash: hash(source + location_id + description_hash + time_bucket)
    # Computed by the ingestion service before insert.
    dedup_key: Mapped[str | None] = mapped_column(
        String(128), nullable=True, unique=True,
        comment="Composite dedup hash to prevent duplicate event ingestion",
    )

    # Relationships
    incident = relationship("Incident", back_populates="events")
    location = relationship("Location", back_populates="events")

    __table_args__ = (
        Index("ix_events_dedup_key", "dedup_key", unique=True),
        Index("ix_events_incident_id", "incident_id"),
        Index("ix_events_created_at", "created_at"),
    )
