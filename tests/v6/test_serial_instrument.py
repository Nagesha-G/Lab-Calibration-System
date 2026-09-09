import json

from src.v6.hardware.serial_instrument import SerialInstrument


class FakeSerial:
    def __init__(self, data: bytes):
        self.data = data
        self.is_open = True
        self.last_written = None

    def write(self, data: bytes):
        self.last_written = data
        return len(data)

    def flush(self):
        pass

    def readline(self):
        return self.data

    def close(self):
        self.is_open = False


def test_serial_instrument_reads_measurement():
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

    instrument = SerialInstrument("COM_TEST")

    fake_serial = FakeSerial(
        (json.dumps(measurement) + "\n").encode("utf-8")
    )

    instrument._serial = fake_serial

    result = instrument.read_measurement()

    assert result == measurement
    assert fake_serial.last_written == b"READ?\n"


def test_serial_instrument_rejects_invalid_measurement():
    measurement = {
        "PT08.S1(CO)": 1200,
        "PT08.S2(NMHC)": 1000,
        "PT08.S3(NOx)": 900,
        "PT08.S4(NO2)": 1100,
        "PT08.S5(O3)": 1000,
        "T": 20,
        "RH": 150,
        "AH": 1.0,
    }

    instrument = SerialInstrument("COM_TEST")

    fake_serial = FakeSerial(
        (json.dumps(measurement) + "\n").encode("utf-8")
    )

    instrument._serial = fake_serial

    try:
        instrument.read_measurement()
        assert False, "Invalid measurement should be rejected."
    except ValueError as exc:
        assert "RH" in str(exc)