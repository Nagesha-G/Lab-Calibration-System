import json
from datetime import datetime

from src.v5.database.database import SessionLocal
from src.v5.database.models import Instrument, InstrumentConfiguration


def create_configuration(
    instrument_id: int,
    configuration_name: str,
    input_schema: dict,
    target_variable: str,
    unit: str,
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

        if not configuration_name.strip():
            raise ValueError(
                "Configuration name cannot be empty."
            )

        if not isinstance(input_schema, dict):
            raise ValueError(
                "Input schema must be a dictionary."
            )

        if not input_schema:
            raise ValueError(
                "Input schema cannot be empty."
            )

        if not target_variable.strip():
            raise ValueError(
                "Target variable cannot be empty."
            )

        if not unit.strip():
            raise ValueError(
                "Unit cannot be empty."
            )

        configuration = InstrumentConfiguration(
            instrument_id=instrument_id,
            configuration_name=configuration_name,
            input_schema=json.dumps(input_schema),
            target_variable=target_variable,
            unit=unit,
            active=active,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        db.add(configuration)
        db.commit()
        db.refresh(configuration)

        return configuration

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


def get_configuration(configuration_id: int):
    db = SessionLocal()

    try:
        configuration = (
            db.query(InstrumentConfiguration)
            .filter(
                InstrumentConfiguration.configuration_id
                == configuration_id
            )
            .first()
        )

        return configuration

    finally:
        db.close()


def get_instrument_configurations(instrument_id: int):
    db = SessionLocal()

    try:
        configurations = (
            db.query(InstrumentConfiguration)
            .filter(
                InstrumentConfiguration.instrument_id
                == instrument_id
            )
            .all()
        )

        return configurations

    finally:
        db.close()


def get_active_configuration(instrument_id: int):
    db = SessionLocal()

    try:
        configuration = (
            db.query(InstrumentConfiguration)
            .filter(
                InstrumentConfiguration.instrument_id
                == instrument_id,
                InstrumentConfiguration.active == True,
            )
            .first()
        )

        return configuration

    finally:
        db.close()