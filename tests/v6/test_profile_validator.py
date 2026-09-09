import pytest

from src.v6.hardware.instrument_profile import (
    InstrumentProfile,
    MeasurementField,
)
from src.v6.hardware.profile_validator import (
    validate_profile_measurement,
)


def create_profile():
    return InstrumentProfile(
        manufacturer="Example Instruments",
        model="GA-500",
        serial_number="GA-500-001",
        transport_type="serial",
        read_command="MEAS?",
        connection={"port": "COM_TEST"},
        measurement_fields=[
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


def test_valid_measurement():
    profile = create_profile()

    measurement = {
        "T": 25,
        "RH": 50,
    }

    result = validate_profile_measurement(
        profile,
        measurement,
    )

    assert result == measurement


def test_missing_field_rejected():
    profile = create_profile()

    with pytest.raises(ValueError, match="Missing"):
        validate_profile_measurement(
            profile,
            {"T": 25},
        )


def test_non_numeric_value_rejected():
    profile = create_profile()

    with pytest.raises(ValueError, match="numeric"):
        validate_profile_measurement(
            profile,
            {
                "T": "25",
                "RH": 50,
            },
        )


def test_out_of_range_value_rejected():
    profile = create_profile()

    with pytest.raises(ValueError, match="RH"):
        validate_profile_measurement(
            profile,
            {
                "T": 25,
                "RH": 150,
            },
        )