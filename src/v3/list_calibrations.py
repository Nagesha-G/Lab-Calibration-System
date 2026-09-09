from src.v3.database import SessionLocal
from src.v3.models import CalibrationRecord


db = SessionLocal()

try:
    records = (
        db.query(CalibrationRecord)
        .order_by(CalibrationRecord.record_id)
        .all()
    )

    print(f"Total calibration records: {len(records)}")

    for record in records:
        print()
        print(f"Record ID: {record.record_id}")
        print(f"Instrument ID: {record.instrument_id}")
        print(f"Measurement Time: {record.measurement_time}")
        print(f"Model Version: {record.model_version}")
        print(f"Estimated Value: {record.estimated_value}")
        print(f"Reference Value: {record.reference_value}")
        print(f"Error: {record.error}")
        print(f"Tolerance: {record.tolerance}")
        print(f"Status: {record.status}")
        print("----------------------------------------")

finally:
    db.close()