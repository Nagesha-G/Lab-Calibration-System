import pytest

from src.v6.hardware.instrument_config import InstrumentConfig


def valid_config():
    return InstrumentConfig(
        manufacturer="Example Instruments",
        model="GA-100",
        serial_number="GA-TEST-001",
        transport_type="serial",
        read_command="MEAS?",
        connection={
            "port": "COM_TEST",
            "baudrate": 9600,
        },
        measurement_fields=[
            "PT08.S1(CO)",
            "PT08.S2(NMHC)",
            "PT08.S3(NOx)",
            "PT08.S4(NO2)",
            "PT08.S5(O3)",
            "T",
            "RH",
            "AH",
        ],
    )


def test_valid_configuration():
    config = valid_config()

    assert config.validate() is True


def test_empty_manufacturer_rejected():
    config = valid_config()
    config.manufacturer = ""

    with pytest.raises(ValueError, match="manufacturer"):
        config.validate()


def test_invalid_transport_rejected():
    config = valid_config()
    config.transport_type = "bluetooth"

    with pytest.raises(ValueError, match="Unsupported transport"):
        config.validate()


def test_empty_measurement_fields_rejected():
    config = valid_config()
    config.measurement_fields = []

    with pytest.raises(ValueError, match="measurement_fields"):
        config.validate()