import json

import pytest

from src.v6.hardware.usb_protocol import (
    decode_usb_measurement,
    encode_usb_measurement,
)


def test_usb_encode_decode():
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

    encoded = encode_usb_measurement(measurement)
    decoded = decode_usb_measurement(encoded)

    assert decoded == measurement


def test_usb_invalid_humidity_rejected():
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

    with pytest.raises(ValueError, match="RH"):
        decode_usb_measurement(
            json.dumps(measurement).encode("utf-8")
        )


def test_usb_empty_message_rejected():
    with pytest.raises(ValueError, match="empty"):
        decode_usb_measurement(b"")