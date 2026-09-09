from datetime import datetime

from src.v5.database.database import SessionLocal
from src.v5.database.models import AuditLog, User


def create_audit_log(
    action: str,
    entity_type: str,
    entity_id: int,
    details: str | None = None,
    user_id: int | None = None,
):
    db = SessionLocal()

    try:
        if not action.strip():
            raise ValueError(
                "Audit action cannot be empty."
            )

        if not entity_type.strip():
            raise ValueError(
                "Entity type cannot be empty."
            )

        if entity_id < 1:
            raise ValueError(
                "Entity ID must be greater than 0."
            )

        if user_id is not None:
            user = (
                db.query(User)
                .filter(
                    User.user_id == user_id
                )
                .first()
            )

            if user is None:
                raise ValueError(
                    f"User {user_id} does not exist."
                )

        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details,
            created_at=datetime.now(),
        )

        db.add(audit_log)
        db.commit()
        db.refresh(audit_log)

        return audit_log

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


def get_audit_log(audit_id: int):
    db = SessionLocal()

    try:
        audit_log = (
            db.query(AuditLog)
            .filter(
                AuditLog.audit_id == audit_id
            )
            .first()
        )

        return audit_log

    finally:
        db.close()


def get_entity_audit_logs(
    entity_type: str,
    entity_id: int,
):
    db = SessionLocal()

    try:
        audit_logs = (
            db.query(AuditLog)
            .filter(
                AuditLog.entity_type == entity_type,
                AuditLog.entity_id == entity_id,
            )
            .order_by(
                AuditLog.created_at.desc()
            )
            .all()
        )

        return audit_logs

    finally:
        db.close()


def get_user_audit_logs(user_id: int):
    db = SessionLocal()

    try:
        audit_logs = (
            db.query(AuditLog)
            .filter(
                AuditLog.user_id == user_id
            )
            .order_by(
                AuditLog.created_at.desc()
            )
            .all()
        )

        return audit_logs

    finally:
        db.close()