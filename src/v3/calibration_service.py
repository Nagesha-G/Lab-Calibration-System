from datetime import datetime

from src.v3.database import SessionLocal
from src.v3.models import CalibrationRecord


def save_calibration(
    instrument_id: int,
    model_version: str,
    estimated_value: float,
    reference_value: float,
    tolerance: float
):
    if reference_value <= 0:
        raise ValueError("Reference value must be greater than 0.")

    if estimated_value < 0:
        raise ValueError("Estimated value cannot be negative.")

    if tolerance < 0:
        raise ValueError("Tolerance cannot be negative.")

    error = estimated_value - reference_value
    absolute_error = abs(error)

    status = "PASS" if absolute_error <= tolerance else "FAIL"

    db = SessionLocal()

    try:
        record = CalibrationRecord(
            instrument_id=instrument_id,
            measurement_time=datetime.now(),
            model_version=model_version,
            estimated_value=estimated_value,
            reference_value=reference_value,
            error=error,
            tolerance=tolerance,
            status=status
        )

        db.add(record)
        db.commit()
        db.refresh(record)

        return record

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()