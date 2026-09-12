"""Team model — group of people available for task assignment."""

import uuid

from sqlalchemy import String, Integer, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Team(Base):
    __tablename__ = "teams"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    team_type: Mapped[str] = mapped_column(
        String(64), nullable=False,
        comment="medical | logistics | search_rescue | communication | water | shelter",
    )
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default="available",
        comment="available | deployed | standby | off_duty",
    )
    location_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("locations.id"), nullable=True
    )
    capacity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    metadata_: Mapped[dict | None] = mapped_column(
        "metadata", JSON, nullable=True, default=dict
    )

    # Relationships
    location = relationship("Location", back_populates="teams")
    assignments = relationship("Assignment", back_populates="team", lazy="selectin")
