import json

from src.v6.hardware.instrument_interface import InstrumentInterface
from src.v6.hardware.instrument_profile import (
    InstrumentProfile,
    MeasurementField,
)
from src.v6.hardware.profile_adapter import ProfileDrivenAdapter


class FakeTransport(InstrumentInterface):
    def __init__(self, response: bytes):
        self.response = response
        self.connected = False
        self.last_command = None

    def connect(self):
        self.connected = True

    def disconnect(self):
        self.connected = False

    def is_connected(self) -> bool:
        return self.connected

    def read_measurement(self) -> dict:
        raise NotImplementedError

    def send_command(self, command: str) -> bytes:
        if not self.connected:
            raise RuntimeError("Transport not connected.")

        self.last_command = command

        return self.response


def create_profile():
    return InstrumentProfile(
        manufacturer="Example Instruments",
        model="GA-500",
        serial_number="GA-500-001",
        transport_type="serial",
        read_command="MEAS?",
        connection={
            "port": "COM_TEST",
        },
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


def test_profile_driven_adapter_reads_valid_measurement():
    measurement = {
        "T": 25,
        "RH": 50,
    }

    transport = FakeTransport(
        json.dumps(measurement).encode("utf-8")
    )

    adapter = ProfileDrivenAdapter(
        transport=transport,
        profile=create_profile(),
    )

    adapter.connect()

    result = adapter.read_measurement()

    assert result == measurement
    assert transport.last_command == "MEAS?"


def test_profile_driven_adapter_rejects_invalid_measurement():
    measurement = {
        "T": 25,
        "RH": 150,
    }

    transport = FakeTransport(
        json.dumps(measurement).encode("utf-8")
    )

    adapter = ProfileDrivenAdapter(
        transport=transport,
        profile=create_profile(),
    )

    adapter.connect()

    try:
        adapter.read_measurement()
        assert False, "Invalid measurement should be rejected."
    except ValueError as exc:
        assert "RH" in str(exc)


def test_profile_driven_adapter_identifies_instrument():
    transport = FakeTransport(b"{}")

    adapter = ProfileDrivenAdapter(
        transport=transport,
        profile=create_profile(),
    )

    identity = adapter.identify()

    assert identity["manufacturer"] == "Example Instruments"
    assert identity["model"] == "GA-500"
    assert identity["serial_number"] == "GA-500-001"
    assert identity["transport_type"] == "serial"