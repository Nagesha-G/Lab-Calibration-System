import pytest
from datetime import datetime

from src.v5.database.database import SessionLocal
from src.v5.database.models import Instrument
from src.v5.services.policy_service import (
    create_policy,
    get_policy,
    get_instrument_policies,
    get_active_policy,
    calculate_next_calibration_date,
    get_calibration_status,
)


def create_test_instrument():
    db = SessionLocal()

    instrument = Instrument(
        name="Test Policy Instrument",
        manufacturer="Test Manufacturer",
        model="PI-100",
        serial_number="POLICY-TEST-001",
        instrument_type="gas_analyzer",
        status="active",
    )

    db.add(instrument)
    db.commit()
    db.refresh(instrument)

    instrument_id = instrument.instrument_id

    db.close()

    return instrument_id


def delete_test_instrument(instrument_id):
    db = SessionLocal()

    instrument = (
        db.query(Instrument)
        .filter(
            Instrument.instrument_id == instrument_id
        )
        .first()
    )

    if instrument:
        db.delete(instrument)
        db.commit()

    db.close()


def test_create_policy():
    instrument_id = create_test_instrument()

    try:
        policy = create_policy(
            instrument_id=instrument_id,
            calibration_interval_days=30,
            tolerance=0.5,
            reference_required=True,
            active=True,
        )

        assert policy.policy_id is not None
        assert policy.instrument_id == instrument_id
        assert policy.calibration_interval_days == 30
        assert policy.tolerance == 0.5
        assert policy.reference_required is True
        assert policy.active is True

    finally:
        delete_test_instrument(instrument_id)


def test_create_policy_invalid_instrument():
    with pytest.raises(ValueError, match="does not exist"):
        create_policy(
            instrument_id=999999,
            calibration_interval_days=30,
            tolerance=0.5,
        )


def test_create_policy_invalid_interval():
    instrument_id = create_test_instrument()

    try:
        with pytest.raises(
            ValueError,
            match="at least 1 day",
        ):
            create_policy(
                instrument_id=instrument_id,
                calibration_interval_days=0,
                tolerance=0.5,
            )

    finally:
        delete_test_instrument(instrument_id)


def test_create_policy_invalid_tolerance():
    instrument_id = create_test_instrument()

    try:
        with pytest.raises(
            ValueError,
            match="cannot be negative",
        ):
            create_policy(
                instrument_id=instrument_id,
                calibration_interval_days=30,
                tolerance=-0.1,
            )

    finally:
        delete_test_instrument(instrument_id)


def test_duplicate_active_policy_rejected():
    instrument_id = create_test_instrument()

    try:
        create_policy(
            instrument_id=instrument_id,
            calibration_interval_days=30,
            tolerance=0.5,
            active=True,
        )

        with pytest.raises(
            ValueError,
            match="already has an active calibration policy",
        ):
            create_policy(
                instrument_id=instrument_id,
                calibration_interval_days=60,
                tolerance=1.0,
                active=True,
            )

    finally:
        delete_test_instrument(instrument_id)


def test_inactive_policies_allowed():
    instrument_id = create_test_instrument()

    try:
        policy_1 = create_policy(
            instrument_id=instrument_id,
            calibration_interval_days=30,
            tolerance=0.5,
            active=False,
        )

        policy_2 = create_policy(
            instrument_id=instrument_id,
            calibration_interval_days=60,
            tolerance=1.0,
            active=False,
        )

        assert policy_1.active is False
        assert policy_2.active is False

    finally:
        delete_test_instrument(instrument_id)


def test_get_policy():
    instrument_id = create_test_instrument()

    try:
        policy = create_policy(
            instrument_id=instrument_id,
            calibration_interval_days=30,
            tolerance=0.5,
        )

        result = get_policy(policy.policy_id)

        assert result is not None
        assert result.policy_id == policy.policy_id
        assert result.tolerance == 0.5

    finally:
        delete_test_instrument(instrument_id)


def test_get_instrument_policies():
    instrument_id = create_test_instrument()

    try:
        create_policy(
            instrument_id=instrument_id,
            calibration_interval_days=30,
            tolerance=0.5,
            active=False,
        )

        create_policy(
            instrument_id=instrument_id,
            calibration_interval_days=60,
            tolerance=1.0,
            active=False,
        )

        policies = get_instrument_policies(
            instrument_id
        )

        assert len(policies) == 2

    finally:
        delete_test_instrument(instrument_id)


def test_get_active_policy():
    instrument_id = create_test_instrument()

    try:
        policy = create_policy(
            instrument_id=instrument_id,
            calibration_interval_days=30,
            tolerance=0.5,
            active=True,
        )

        result = get_active_policy(instrument_id)

        assert result is not None
        assert result.policy_id == policy.policy_id
        assert result.active is True

    finally:
        delete_test_instrument(instrument_id)


def test_calculate_next_calibration_date():
    last_date = datetime(2026, 9, 1)

    next_date = calculate_next_calibration_date(
        last_calibration_date=last_date,
        calibration_interval_days=30,
    )

    assert next_date == datetime(2026, 10, 1)


def test_calculate_next_calibration_invalid_interval():
    last_date = datetime(2026, 9, 1)

    with pytest.raises(
        ValueError,
        match="at least 1 day",
    ):
        calculate_next_calibration_date(
            last_calibration_date=last_date,
            calibration_interval_days=0,
        )


def test_calibration_status_current():
    next_date = datetime(2026, 10, 1)
    current_date = datetime(2026, 9, 15)

    status = get_calibration_status(
        next_calibration_date=next_date,
        current_date=current_date,
    )

    assert status == "CURRENT"


def test_calibration_status_overdue():
    next_date = datetime(2026, 10, 1)
    current_date = datetime(2026, 10, 2)

    status = get_calibration_status(
        next_calibration_date=next_date,
        current_date=current_date,
    )

    assert status == "OVERDUE"


def test_calibration_status_due_today():
    next_date = datetime(2026, 10, 1)
    current_date = datetime(2026, 10, 1)

    status = get_calibration_status(
        next_calibration_date=next_date,
        current_date=current_date,
    )

    assert status == "OVERDUE"