"""AuditLog model — immutable record of every significant action."""

import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, Index, JSON, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    entity_type: Mapped[str] = mapped_column(
        String(64), nullable=False,
        comment="Table/domain name: incident, plan, task, resource, …",
    )
    entity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False
    )
    action: Mapped[str] = mapped_column(
        String(64), nullable=False,
        comment="created | updated | assigned | completed | replanned | escalated | …",
    )
    actor: Mapped[str] = mapped_column(
        String(128), nullable=False,
        comment="Agent name, user ID, or 'system'",
    )
    details: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        Index("ix_audit_logs_entity", "entity_type", "entity_id"),
        Index("ix_audit_logs_created_at", "created_at"),
    )
