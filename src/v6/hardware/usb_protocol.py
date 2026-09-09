from src.v6.hardware.serial_protocol import validate_measurement
import json


def encode_usb_measurement(measurement: dict) -> bytes:
    return json.dumps(measurement).encode("utf-8")


def decode_usb_measurement(data: bytes) -> dict:
    if not data:
        raise ValueError("Received empty USB message.")

    try:
        measurement = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("Invalid USB measurement message.") from exc

    return validate_measurement(measurement)