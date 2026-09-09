import pytest

from src.v5.database.database import SessionLocal
from src.v5.database.models import Instrument
from src.v5.services.measurement_service import (
    create_measurement,
    get_measurement,
    get_instrument_measurements,
    parse_measurement_data,
)


def create_test_instrument():
    db = SessionLocal()

    instrument = Instrument(
        name="Test Measurement Instrument",
        manufacturer="Test Manufacturer",
        model="MI-100",
        serial_number="MEASUREMENT-TEST-001",
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
        .filter(
            Instrument.instrument_id == instrument_id
        )
        .first()
    )

    if instrument:
        db.delete(instrument)
        db.commit()

    db.close()


def test_create_measurement():
    instrument_id = create_test_instrument()

    try:
        measurement_data = {
            "sensor_1": 1200.5,
            "sensor_2": 950.2,
            "temperature": 25.4,
            "humidity": 48.2,
        }

        measurement = create_measurement(
            instrument_id=instrument_id,
            measurement_data=measurement_data,
        )

        assert measurement.measurement_id is not None
        assert measurement.instrument_id == instrument_id
        assert measurement.measurement_data is not None
        assert measurement.created_at is not None

    finally:
        delete_test_instrument(instrument_id)


def test_create_measurement_invalid_instrument():
    with pytest.raises(ValueError, match="does not exist"):
        create_measurement(
            instrument_id=999999,
            measurement_data={
                "sensor_1": 100
            },
        )


def test_create_measurement_empty_data():
    instrument_id = create_test_instrument()

    try:
        with pytest.raises(
            ValueError,
            match="cannot be empty",
        ):
            create_measurement(
                instrument_id=instrument_id,
                measurement_data={},
            )

    finally:
        delete_test_instrument(instrument_id)


def test_create_measurement_non_dictionary():
    instrument_id = create_test_instrument()

    try:
        with pytest.raises(
            ValueError,
            match="must be a dictionary",
        ):
            create_measurement(
                instrument_id=instrument_id,
                measurement_data=["invalid"],
            )

    finally:
        delete_test_instrument(instrument_id)


def test_get_measurement():
    instrument_id = create_test_instrument()

    try:
        measurement = create_measurement(
            instrument_id=instrument_id,
            measurement_data={
                "sensor_1": 500
            },
        )

        result = get_measurement(
            measurement.measurement_id
        )

        assert result is not None
        assert (
            result.measurement_id
            == measurement.measurement_id
        )
        assert (
            result.instrument_id
            == instrument_id
        )

    finally:
        delete_test_instrument(instrument_id)


def test_get_instrument_measurements():
    instrument_id = create_test_instrument()

    try:
        create_measurement(
            instrument_id=instrument_id,
            measurement_data={
                "sensor_1": 100
            },
        )

        create_measurement(
            instrument_id=instrument_id,
            measurement_data={
                "sensor_1": 200
            },
        )

        measurements = get_instrument_measurements(
            instrument_id
        )

        assert len(measurements) == 2
        assert (
            measurements[0].created_at
            >= measurements[1].created_at
        )

    finally:
        delete_test_instrument(instrument_id)


def test_parse_measurement_data():
    instrument_id = create_test_instrument()

    try:
        measurement_data = {
            "sensor_1": 1200.5,
            "sensor_2": 950.2,
            "temperature": 25.4,
        }

        measurement = create_measurement(
            instrument_id=instrument_id,
            measurement_data=measurement_data,
        )

        parsed_data = parse_measurement_data(
            measurement
        )

        assert parsed_data == measurement_data

    finally:
        delete_test_instrument(instrument_id)


def test_parse_missing_measurement():
    with pytest.raises(
        ValueError,
        match="does not exist",
    ):
        parse_measurement_data(None)