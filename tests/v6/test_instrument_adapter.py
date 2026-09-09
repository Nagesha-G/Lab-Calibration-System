import json

from src.v6.hardware.configured_adapter import (
    ConfiguredInstrumentAdapter,
)
from src.v6.hardware.instrument_interface import InstrumentInterface


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
        self.last_command = command

        if not self.connected:
            raise RuntimeError("Transport not connected.")

        return self.response


def test_adapter_connects_through_transport():
    transport = FakeTransport(
        b'{"PT08.S1(CO)":1200,"PT08.S2(NMHC)":1000,'
        b'"PT08.S3(NOx)":900,"PT08.S4(NO2)":1100,'
        b'"PT08.S5(O3)":1000,"T":20,"RH":50,"AH":1.0}'
    )

    adapter = ConfiguredInstrumentAdapter(
        transport=transport,
        identity={
            "manufacturer": "Example",
            "model": "GA-100",
        },
    )

    adapter.connect()

    assert adapter.is_connected() is True


def test_adapter_identifies_instrument():
    transport = FakeTransport(b"{}")

    adapter = ConfiguredInstrumentAdapter(
        transport=transport,
        identity={
            "manufacturer": "Example",
            "model": "GA-100",
            "serial_number": "TEST-001",
        },
    )

    identity = adapter.identify()

    assert identity["manufacturer"] == "Example"
    assert identity["model"] == "GA-100"
    assert identity["serial_number"] == "TEST-001"


def test_adapter_sends_configured_read_command():
    measurement = {
        "PT08.S1(CO)": 1200,
        "PT08.S2(NMHC)": 1000,
        "PT08.S3(NOx)": 900,
        "PT08.S4(NO2)": 1100,
        "PT08.S5(O3)": 1000,
        "T": 20,
        "RH": 50,
        "AH": 1.0,
    }

    transport = FakeTransport(
        json.dumps(measurement).encode("utf-8")
    )

    adapter = ConfiguredInstrumentAdapter(
        transport=transport,
        identity={"manufacturer": "Example"},
        read_command="MEAS?",
    )

    adapter.connect()

    result = adapter.read_measurement()

    assert result == measurement
    assert transport.last_command == "MEAS?"


def test_adapter_requires_connected_transport():
    transport = FakeTransport(b"{}")

    adapter = ConfiguredInstrumentAdapter(
        transport=transport,
        identity={"manufacturer": "Example"},
    )

    try:
        adapter.read_measurement()
        assert False, "Disconnected adapter should be rejected."
    except RuntimeError as exc:
        assert "not connected" in str(exc)