import json
from datetime import datetime

from src.v5.database.database import SessionLocal
from src.v5.database.models import Instrument, Measurement


def create_measurement(
    instrument_id: int,
    measurement_data: dict,
):
    db = SessionLocal()

    try:
        instrument = (
            db.query(Instrument)
            .filter(
                Instrument.instrument_id == instrument_id
            )
            .first()
        )

        if instrument is None:
            raise ValueError(
                f"Instrument {instrument_id} does not exist."
            )

        if not isinstance(measurement_data, dict):
            raise ValueError(
                "Measurement data must be a dictionary."
            )

        if not measurement_data:
            raise ValueError(
                "Measurement data cannot be empty."
            )

        measurement = Measurement(
            instrument_id=instrument_id,
            measurement_data=json.dumps(
                measurement_data
            ),
            created_at=datetime.now(),
        )

        db.add(measurement)
        db.commit()
        db.refresh(measurement)

        return measurement

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


def get_measurement(measurement_id: int):
    db = SessionLocal()

    try:
        measurement = (
            db.query(Measurement)
            .filter(
                Measurement.measurement_id
                == measurement_id
            )
            .first()
        )

        return measurement

    finally:
        db.close()


def get_instrument_measurements(instrument_id: int):
    db = SessionLocal()

    try:
        measurements = (
            db.query(Measurement)
            .filter(
                Measurement.instrument_id
                == instrument_id
            )
            .order_by(
                Measurement.created_at.desc()
            )
            .all()
        )

        return measurements

    finally:
        db.close()


def parse_measurement_data(
    measurement: Measurement,
):
    if measurement is None:
        raise ValueError(
            "Measurement does not exist."
        )

    return json.loads(
        measurement.measurement_data
    )