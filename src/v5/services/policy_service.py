from datetime import datetime, timedelta

from src.v5.database.database import SessionLocal
from src.v5.database.models import Instrument, CalibrationPolicy


def create_policy(
    instrument_id: int,
    calibration_interval_days: int,
    tolerance: float,
    reference_required: bool = True,
    active: bool = True,
):
    db = SessionLocal()

    try:
        instrument = (
            db.query(Instrument)
            .filter(Instrument.instrument_id == instrument_id)
            .first()
        )

        if instrument is None:
            raise ValueError(
                f"Instrument {instrument_id} does not exist."
            )

        if calibration_interval_days < 1:
            raise ValueError(
                "Calibration interval must be at least 1 day."
            )

        if tolerance < 0:
            raise ValueError(
                "Tolerance cannot be negative."
            )

        existing_policy = (
            db.query(CalibrationPolicy)
            .filter(
                CalibrationPolicy.instrument_id == instrument_id,
                CalibrationPolicy.active == True,
            )
            .first()
        )

        if active and existing_policy is not None:
            raise ValueError(
                "Instrument already has an active calibration policy."
            )

        policy = CalibrationPolicy(
            instrument_id=instrument_id,
            calibration_interval_days=calibration_interval_days,
            tolerance=tolerance,
            reference_required=reference_required,
            active=active,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        db.add(policy)
        db.commit()
        db.refresh(policy)

        return policy

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


def get_policy(policy_id: int):
    db = SessionLocal()

    try:
        policy = (
            db.query(CalibrationPolicy)
            .filter(
                CalibrationPolicy.policy_id == policy_id
            )
            .first()
        )

        return policy

    finally:
        db.close()


def get_instrument_policies(instrument_id: int):
    db = SessionLocal()

    try:
        policies = (
            db.query(CalibrationPolicy)
            .filter(
                CalibrationPolicy.instrument_id == instrument_id
            )
            .all()
        )

        return policies

    finally:
        db.close()


def get_active_policy(instrument_id: int):
    db = SessionLocal()

    try:
        policy = (
            db.query(CalibrationPolicy)
            .filter(
                CalibrationPolicy.instrument_id == instrument_id,
                CalibrationPolicy.active == True,
            )
            .first()
        )

        return policy

    finally:
        db.close()


def calculate_next_calibration_date(
    last_calibration_date: datetime,
    calibration_interval_days: int,
):
    if calibration_interval_days < 1:
        raise ValueError(
            "Calibration interval must be at least 1 day."
        )

    return (
        last_calibration_date
        + timedelta(days=calibration_interval_days)
    )


def get_calibration_status(
    next_calibration_date: datetime,
    current_date: datetime | None = None,
):
    if current_date is None:
        current_date = datetime.now()

    if current_date >= next_calibration_date:
        return "OVERDUE"

    return "CURRENT"