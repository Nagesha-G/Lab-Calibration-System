from datetime import datetime, timedelta

from src.v3.database import SessionLocal
from src.v3.models import Instrument


def get_due_instruments(days: int = 30):
    db = SessionLocal()

    try:
        cutoff_date = datetime.now() - timedelta(days=days)

        instruments = (
            db.query(Instrument)
            .filter(Instrument.status == "active")
            .all()
        )

        due_instruments = []

        for instrument in instruments:

            if not instrument.calibration_records:
                due_instruments.append({
                    "instrument_id": instrument.instrument_id,
                    "name": instrument.name,
                    "serial_number": instrument.serial_number,
                    "reason": "No calibration records"
                })
                continue

            latest_calibration = max(
                instrument.calibration_records,
                key=lambda record: record.measurement_time
            )

            if latest_calibration.measurement_time <= cutoff_date:
                due_instruments.append({
                    "instrument_id": instrument.instrument_id,
                    "name": instrument.name,
                    "serial_number": instrument.serial_number,
                    "last_calibration": (
                        latest_calibration.measurement_time.isoformat()
                    ),
                    "reason": "Calibration overdue"
                })

        return due_instruments

    finally:
        db.close()