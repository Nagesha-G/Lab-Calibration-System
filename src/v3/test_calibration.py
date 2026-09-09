from datetime import datetime

from src.v3.database import SessionLocal
from src.v3.models import CalibrationRecord


def create_calibration_record():
    db = SessionLocal()

    record = CalibrationRecord(
        instrument_id=1,
        measurement_time=datetime.now(),
        model_version="v2.0.0",
        estimated_value=3.15,
        reference_value=3.10,
        error=3.15 - 3.10
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    print("Calibration record created successfully.")
    print(f"Record ID: {record.record_id}")
    print(f"Instrument ID: {record.instrument_id}")
    print(f"Model Version: {record.model_version}")
    print(f"Estimated Value: {record.estimated_value}")
    print(f"Reference Value: {record.reference_value}")
    print(f"Error: {record.error}")

    db.close()


if __name__ == "__main__":
    create_calibration_record()