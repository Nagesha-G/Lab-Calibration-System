import json

import pytest

from src.v6.hardware.tcp_instrument import TCPInstrument


class FakeSocket:
    def __init__(self, response: bytes):
        self.response = response
        self.sent_data = None
        self.closed = False

    def sendall(self, data: bytes):
        self.sent_data = data

    def recv(self, buffer_size: int):
        return self.response

    def close(self):
        self.closed = True


def test_tcp_instrument_reads_measurement():
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

    response = json.dumps(measurement).encode("utf-8")

    instrument = TCPInstrument(
        host="127.0.0.1",
        port=5000,
    )

    fake_socket = FakeSocket(response)
    instrument._socket = fake_socket

    result = instrument.read_measurement()

    assert result == measurement
    assert fake_socket.sent_data == b"READ?\n"


def test_tcp_instrument_rejects_empty_command():
    instrument = TCPInstrument(
        host="127.0.0.1",
        port=5000,
    )

    instrument._socket = FakeSocket(b"{}")

    with pytest.raises(ValueError, match="Command cannot be empty"):
        instrument.send_command("   ")


def test_tcp_instrument_requires_connection():
    instrument = TCPInstrument(
        host="127.0.0.1",
        port=5000,
    )

    with pytest.raises(RuntimeError, match="not connected"):
        instrument.send_command("READ?")