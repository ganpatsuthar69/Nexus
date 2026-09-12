"""Resource model — physical asset available for assignment."""

import uuid
from datetime import datetime

from sqlalchemy import String, Integer, DateTime, ForeignKey, JSON, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Resource(Base):
    __tablename__ = "resources"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    resource_type: Mapped[str] = mapped_column(
        String(64), nullable=False,
        comment="water_tanker | generator | medical_kit | food_supply | shelter | vehicle | …",
    )
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default="available",
        comment="available | assigned | in_transit | depleted | maintenance",
    )
    capacity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    location_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("locations.id"), nullable=True
    )
    metadata_: Mapped[dict | None] = mapped_column(
        "metadata", JSON, nullable=True, default=dict
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    location = relationship("Location", back_populates="resources")
    assignments = relationship("Assignment", back_populates="resource", lazy="selectin")
