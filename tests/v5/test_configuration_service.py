import json

import pytest

from src.v5.database.database import SessionLocal
from src.v5.database.models import Instrument, InstrumentConfiguration
from src.v5.services.configuration_service import (
    create_configuration,
    get_configuration,
    get_instrument_configurations,
    get_active_configuration,
)


def create_test_instrument():
    db = SessionLocal()

    instrument = Instrument(
        name="Test Gas Analyzer",
        manufacturer="Test Manufacturer",
        model="GA-100",
        serial_number="CONFIG-TEST-001",
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
        .filter(Instrument.instrument_id == instrument_id)
        .first()
    )

    if instrument:
        db.delete(instrument)
        db.commit()

    db.close()


def test_create_configuration():
    instrument_id = create_test_instrument()

    try:
        input_schema = {
            "sensor_1": "PT08.S1(CO)",
            "sensor_2": "PT08.S2(NMHC)",
            "temperature": "T",
        }

        configuration = create_configuration(
            instrument_id=instrument_id,
            configuration_name="CO Calibration",
            input_schema=input_schema,
            target_variable="CO(GT)",
            unit="mg/m3",
        )

        assert configuration.configuration_id is not None
        assert configuration.instrument_id == instrument_id
        assert configuration.configuration_name == "CO Calibration"
        assert configuration.target_variable == "CO(GT)"
        assert configuration.unit == "mg/m3"
        assert configuration.active is True

        stored_schema = json.loads(configuration.input_schema)

        assert stored_schema == input_schema

    finally:
        delete_test_instrument(instrument_id)


def test_create_configuration_invalid_instrument():
    with pytest.raises(ValueError, match="does not exist"):
        create_configuration(
            instrument_id=999999,
            configuration_name="CO Calibration",
            input_schema={"sensor_1": "PT08.S1(CO)"},
            target_variable="CO(GT)",
            unit="mg/m3",
        )


def test_create_configuration_empty_schema():
    instrument_id = create_test_instrument()

    try:
        with pytest.raises(ValueError, match="cannot be empty"):
            create_configuration(
                instrument_id=instrument_id,
                configuration_name="CO Calibration",
                input_schema={},
                target_variable="CO(GT)",
                unit="mg/m3",
            )

    finally:
        delete_test_instrument(instrument_id)


def test_create_configuration_empty_name():
    instrument_id = create_test_instrument()

    try:
        with pytest.raises(ValueError, match="cannot be empty"):
            create_configuration(
                instrument_id=instrument_id,
                configuration_name="",
                input_schema={"sensor_1": "PT08.S1(CO)"},
                target_variable="CO(GT)",
                unit="mg/m3",
            )

    finally:
        delete_test_instrument(instrument_id)


def test_get_configuration():
    instrument_id = create_test_instrument()

    try:
        configuration = create_configuration(
            instrument_id=instrument_id,
            configuration_name="CO Calibration",
            input_schema={"sensor_1": "PT08.S1(CO)"},
            target_variable="CO(GT)",
            unit="mg/m3",
        )

        result = get_configuration(
            configuration.configuration_id
        )

        assert result is not None
        assert result.configuration_id == configuration.configuration_id
        assert result.configuration_name == "CO Calibration"

    finally:
        delete_test_instrument(instrument_id)


def test_get_instrument_configurations():
    instrument_id = create_test_instrument()

    try:
        create_configuration(
            instrument_id=instrument_id,
            configuration_name="CO Calibration",
            input_schema={"sensor_1": "PT08.S1(CO)"},
            target_variable="CO(GT)",
            unit="mg/m3",
        )

        create_configuration(
            instrument_id=instrument_id,
            configuration_name="Temperature Calibration",
            input_schema={"temperature": "T"},
            target_variable="Temperature",
            unit="C",
        )

        configurations = get_instrument_configurations(
            instrument_id
        )

        assert len(configurations) == 2

    finally:
        delete_test_instrument(instrument_id)


def test_get_active_configuration():
    instrument_id = create_test_instrument()

    try:
        create_configuration(
            instrument_id=instrument_id,
            configuration_name="Inactive Configuration",
            input_schema={"sensor_1": "PT08.S1(CO)"},
            target_variable="CO(GT)",
            unit="mg/m3",
            active=False,
        )

        active_configuration = create_configuration(
            instrument_id=instrument_id,
            configuration_name="Active Configuration",
            input_schema={"sensor_1": "PT08.S1(CO)"},
            target_variable="CO(GT)",
            unit="mg/m3",
            active=True,
        )

        result = get_active_configuration(instrument_id)

        assert result is not None
        assert result.configuration_id == active_configuration.configuration_id
        assert result.active is True

    finally:
        delete_test_instrument(instrument_id)