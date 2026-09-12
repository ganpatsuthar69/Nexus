"""Audit logging service.

Helper functions to record state changes in the audit_logs table.
"""

from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.models import AuditLog


def log_action(
    db: Session,
    entity_type: str,
    entity_id: UUID,
    action: str,
    actor: str,
    details: dict[str, Any] | None = None,
) -> None:
    """Records an immutable audit log entry for a given action."""
    audit = AuditLog(
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        actor=actor,
        details=details,
    )
    db.add(audit)
    # Note: We do not commit here. The caller should commit the transaction
    # containing both the state change and the audit log.
