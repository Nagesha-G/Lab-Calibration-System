import pytest

from src.v6.hardware.serial_instrument import SerialInstrument


class TimeoutSerial:
    def __init__(self):
        self.is_open = True

    def write(self, data: bytes):
        return len(data)

    def flush(self):
        pass

    def readline(self):
        return b""

    def close(self):
        self.is_open = False


class ClosedSerial:
    def __init__(self):
        self.is_open = False


def test_serial_timeout():
    instrument = SerialInstrument("COM_TEST")
    instrument._serial = TimeoutSerial()

    with pytest.raises(TimeoutError):
        instrument.send_command("READ?")


def test_serial_closed_connection():
    instrument = SerialInstrument("COM_TEST")
    instrument._serial = ClosedSerial()

    with pytest.raises(RuntimeError):
        instrument.send_command("READ?")


def test_invalid_serial_response():
    instrument = SerialInstrument("COM_TEST")
    fake_serial = TimeoutSerial()

    fake_serial.readline = lambda: b"not-valid-json\n"

    instrument._serial = fake_serial

    with pytest.raises(ValueError):
        instrument.read_measurement()