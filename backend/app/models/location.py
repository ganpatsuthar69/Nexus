"""Location model — geographical point relevant to coordination."""

import uuid

from sqlalchemy import String, Float, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Location(Base):
    __tablename__ = "locations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    population: Mapped[int | None] = mapped_column(Integer, nullable=True)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    current_status: Mapped[str] = mapped_column(
        String(64), nullable=False, default="normal",
        comment="normal | affected | evacuated | sheltering",
    )

    # Relationships
    events = relationship("Event", back_populates="location", lazy="selectin")
    resources = relationship("Resource", back_populates="location", lazy="selectin")
    teams = relationship("Team", back_populates="location", lazy="selectin")
