"""Policy model — authorization boundary for agent actions.

Defines which action types can be auto-approved and which require
human review, per docs/architecture.md hardening notes.
"""

import uuid

from sqlalchemy import String, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Policy(Base):
    __tablename__ = "policies"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    action_type: Mapped[str] = mapped_column(
        String(64), nullable=False, unique=True,
        comment="assign_resource | reassign_resource | evacuate | notify | mark_duplicate | …",
    )
    max_impact_scope: Mapped[str | None] = mapped_column(
        String(64), nullable=True,
        comment="single_resource | single_location | multi_location | city_wide",
    )
    requires_human: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    auto_approve_conditions: Mapped[dict | None] = mapped_column(
        JSON, nullable=True,
        comment="JSON conditions under which the action can proceed without human review",
    )
