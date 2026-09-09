import pytest

from src.v5.database.database import SessionLocal
from src.v5.database.models import User
from src.v5.services.audit_service import (
    create_audit_log,
    get_audit_log,
    get_entity_audit_logs,
    get_user_audit_logs,
)


def create_test_user():
    db = SessionLocal()

    user = User(
        username="audit_test_user",
        email="audit_test@example.com",
        password_hash="test_hash",
        role="admin",
        status="active",
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    user_id = user.user_id

    db.close()

    return user_id


def delete_test_user(user_id):
    db = SessionLocal()

    user = (
        db.query(User)
        .filter(
            User.user_id == user_id
        )
        .first()
    )

    if user:
        db.delete(user)
        db.commit()

    db.close()


def test_create_audit_log():
    user_id = create_test_user()

    try:
        audit_log = create_audit_log(
            action="CALIBRATION_EXECUTED",
            entity_type="CalibrationRecord",
            entity_id=42,
            details="Calibration completed successfully.",
            user_id=user_id,
        )

        assert audit_log.audit_id is not None
        assert audit_log.user_id == user_id
        assert audit_log.action == "CALIBRATION_EXECUTED"
        assert audit_log.entity_type == "CalibrationRecord"
        assert audit_log.entity_id == 42
        assert (
            audit_log.details
            == "Calibration completed successfully."
        )
        assert audit_log.created_at is not None

    finally:
        delete_test_user(user_id)


def test_create_audit_log_without_user():
    audit_log = create_audit_log(
        action="SYSTEM_STARTED",
        entity_type="System",
        entity_id=1,
    )

    try:
        assert audit_log.audit_id is not None
        assert audit_log.user_id is None
        assert audit_log.action == "SYSTEM_STARTED"

    finally:
        db = SessionLocal()

        stored_log = (
            db.query(type(audit_log))
            .filter(
                type(audit_log).audit_id
                == audit_log.audit_id
            )
            .first()
        )

        if stored_log:
            db.delete(stored_log)
            db.commit()

        db.close()


def test_invalid_empty_action():
    with pytest.raises(
        ValueError,
        match="action cannot be empty",
    ):
        create_audit_log(
            action="",
            entity_type="Instrument",
            entity_id=1,
        )


def test_invalid_empty_entity_type():
    with pytest.raises(
        ValueError,
        match="type cannot be empty",
    ):
        create_audit_log(
            action="CREATE",
            entity_type="",
            entity_id=1,
        )


def test_invalid_entity_id():
    with pytest.raises(
        ValueError,
        match="greater than 0",
    ):
        create_audit_log(
            action="CREATE",
            entity_type="Instrument",
            entity_id=0,
        )


def test_invalid_user():
    with pytest.raises(
        ValueError,
        match="does not exist",
    ):
        create_audit_log(
            action="CREATE",
            entity_type="Instrument",
            entity_id=1,
            user_id=999999,
        )


def test_get_audit_log():
    user_id = create_test_user()

    try:
        audit_log = create_audit_log(
            action="INSTRUMENT_CREATED",
            entity_type="Instrument",
            entity_id=100,
            user_id=user_id,
        )

        result = get_audit_log(
            audit_log.audit_id
        )

        assert result is not None
        assert (
            result.audit_id
            == audit_log.audit_id
        )
        assert (
            result.action
            == "INSTRUMENT_CREATED"
        )

    finally:
        delete_test_user(user_id)


def test_get_entity_audit_logs():
    user_id = create_test_user()

    try:
        create_audit_log(
            action="INSTRUMENT_CREATED",
            entity_type="Instrument",
            entity_id=200,
            user_id=user_id,
        )

        create_audit_log(
            action="INSTRUMENT_UPDATED",
            entity_type="Instrument",
            entity_id=200,
            user_id=user_id,
        )

        logs = get_entity_audit_logs(
            entity_type="Instrument",
            entity_id=200,
        )

        assert len(logs) == 2

        actions = {
            log.action
            for log in logs
        }

        assert actions == {
            "INSTRUMENT_CREATED",
            "INSTRUMENT_UPDATED",
        }

    finally:
        delete_test_user(user_id)


def test_get_user_audit_logs():
    user_id = create_test_user()

    try:
        create_audit_log(
            action="ACTION_ONE",
            entity_type="Instrument",
            entity_id=301,
            user_id=user_id,
        )

        create_audit_log(
            action="ACTION_TWO",
            entity_type="CalibrationRecord",
            entity_id=302,
            user_id=user_id,
        )

        logs = get_user_audit_logs(
            user_id
        )

        assert len(logs) == 2

        actions = {
            log.action
            for log in logs
        }

        assert actions == {
            "ACTION_ONE",
            "ACTION_TWO",
        }

    finally:
        delete_test_user(user_id)