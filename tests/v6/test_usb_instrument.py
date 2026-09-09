import json

import pytest

from src.v6.hardware.usb_instrument import USBInstrument


class FakeUSBDevice:
    def __init__(self, response: bytes):
        self.response = response

    def read(self):
        return self.response


def test_usb_instrument_reads_measurement():
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

    instrument = USBInstrument("USB_TEST_001")
    instrument.connect()

    instrument._device = FakeUSBDevice(
        json.dumps(measurement).encode("utf-8")
    )

    result = instrument.read_measurement()

    assert result == measurement

    instrument.disconnect()


def test_usb_instrument_rejects_empty_response():
    instrument = USBInstrument("USB_TEST_001")
    instrument.connect()

    instrument._device = FakeUSBDevice(b"")

    with pytest.raises(TimeoutError):
        instrument.read_measurement()

    instrument.disconnect()


def test_usb_instrument_requires_device_transport():
    instrument = USBInstrument("USB_TEST_001")
    instrument.connect()

    with pytest.raises(RuntimeError, match="transport"):
        instrument.read_measurement()

    instrument.disconnect()