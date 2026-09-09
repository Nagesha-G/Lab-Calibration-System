import pytest

from src.v6.hardware.instrument_profile import (
    InstrumentProfile,
    MeasurementField,
)


def create_profile():
    return InstrumentProfile(
        manufacturer="Example Instruments",
        model="GA-500",
        serial_number="GA-500-001",
        transport_type="serial",
        read_command="MEAS?",
        connection={
            "port": "COM_TEST",
            "baudrate": 9600,
        },
        measurement_fields=[
            MeasurementField(
                name="PT08.S1(CO)",
                unit="sensor_units",
                minimum=0,
                maximum=5000,
            ),
            MeasurementField(
                name="T",
                unit="degC",
                minimum=-40,
                maximum=85,
            ),
            MeasurementField(
                name="RH",
                unit="%",
                minimum=0,
                maximum=100,
            ),
        ],
    )


def test_valid_profile():
    profile = create_profile()

    assert profile.validate() is True


def test_empty_model_rejected():
    profile = create_profile()
    profile.model = ""

    with pytest.raises(ValueError, match="model"):
        profile.validate()


def test_invalid_transport_rejected():
    profile = create_profile()
    profile.transport_type = "bluetooth"

    with pytest.raises(ValueError, match="Unsupported transport"):
        profile.validate()


def test_invalid_measurement_range_rejected():
    profile = create_profile()

    profile.measurement_fields[0].maximum = 0

    with pytest.raises(
        ValueError,
        match="Invalid range",
    ):
        profile.validate()