from sqlalchemy import desc

from src.v5.database.database import SessionLocal
from src.v5.database.models import CalibrationRecord


def get_instrument_calibration_history(
    instrument_id: int,
    limit: int = 100,
):
    if instrument_id < 1:
        raise ValueError(
            "instrument_id must be greater than 0."
        )

    if limit < 1:
        raise ValueError(
            "limit must be greater than 0."
        )

    db = SessionLocal()

    try:
        records = (
            db.query(CalibrationRecord)
            .filter(
                CalibrationRecord.instrument_id == instrument_id
            )
            .order_by(desc(CalibrationRecord.created_at))
            .limit(limit)
            .all()
        )

        return records

    finally:
        db.close()