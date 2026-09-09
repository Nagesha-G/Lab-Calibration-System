import json

import pytest

from src.v6.hardware.instrument_profile import (
    MeasurementField,
)
from src.v6.hardware.physical_instrument_runtime import (
    PhysicalInstrumentConfig,
    PhysicalInstrumentRuntime,
)


class FakeSerial:
    def __init__(self, response: bytes):
        self.response = response
        self.is_open = True
        self.last_command = None

    def write(self, data: bytes):
        self.last_command = data
        return len(data)

    def flush(self):
        pass

    def readline(self):
        return self.response

    def close(self):
        self.is_open = False


def create_config():
    return PhysicalInstrumentConfig(
        manufacturer="Example Instruments",
        model="GA-500",
        serial_number="GA-500-REAL-001",
        port="COM_TEST",
        baudrate=9600,
        timeout=2.0,
        read_command="MEAS?",
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


def test_physical_config_validates():
    config = create_config()

    assert config.validate() is True


def test_physical_config_rejects_empty_port():
    config = create_config()
    config.port = ""

    with pytest.raises(
        ValueError,
        match="port cannot be empty",
    ):
        config.validate()


def test_runtime_builds_correct_identity():
    runtime = PhysicalInstrumentRuntime(
        create_config()
    )

    identity = runtime.identify()

    assert identity["manufacturer"] == "Example Instruments"
    assert identity["model"] == "GA-500"
    assert identity["serial_number"] == "GA-500-REAL-001"
    assert identity["transport_type"] == "serial"


def test_runtime_reads_valid_measurement():
    measurement = {
        "T": 25,
        "RH": 50,
    }

    runtime = PhysicalInstrumentRuntime(
        create_config()
    )

    fake_serial = FakeSerial(
        json.dumps(measurement).encode("utf-8")
    )

    runtime.transport._serial = fake_serial

    assert runtime.is_connected() is True

    result = runtime.read_measurement()

    assert result == measurement
    assert fake_serial.last_command == b"MEAS?\n"

    runtime.disconnect()

    assert runtime.is_connected() is False


def test_runtime_rejects_invalid_measurement():
    measurement = {
        "T": 25,
        "RH": 150,
    }

    runtime = PhysicalInstrumentRuntime(
        create_config()
    )

    runtime.transport._serial = FakeSerial(
        json.dumps(measurement).encode("utf-8")
    )

    with pytest.raises(
        ValueError,
        match="RH",
    ):
        runtime.read_measurement()

    runtime.disconnect()


def test_runtime_requires_connection():
    runtime = PhysicalInstrumentRuntime(
        create_config()
    )

    with pytest.raises(
        RuntimeError,
        match="not connected",
    ):
        runtime.read_measurement()