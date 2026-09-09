from sqlalchemy import func

from src.v5.database.database import SessionLocal
from src.v5.database.models import CalibrationRecord


def get_calibration_summary(instrument_id: int):
    if instrument_id < 1:
        raise ValueError(
            "instrument_id must be greater than 0."
        )

    db = SessionLocal()

    try:
        records = (
            db.query(CalibrationRecord)
            .filter(
                CalibrationRecord.instrument_id == instrument_id
            )
            .all()
        )

        total = len(records)

        pass_count = sum(
            1 for record in records
            if record.status == "PASS"
        )

        fail_count = sum(
            1 for record in records
            if record.status == "FAIL"
        )

        average_absolute_error = (
            sum(
                record.absolute_error
                for record in records
            ) / total
            if total > 0
            else 0.0
        )

        pass_rate = (
            (pass_count / total) * 100
            if total > 0
            else 0.0
        )

        return {
            "instrument_id": instrument_id,
            "total_calibrations": total,
            "pass_count": pass_count,
            "fail_count": fail_count,
            "pass_rate": round(pass_rate, 4),
            "average_absolute_error": round(
                average_absolute_error,
                10,
            ),
        }

    finally:
        db.close()