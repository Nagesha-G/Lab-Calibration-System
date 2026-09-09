import json


REQUIRED_FIELDS = {
    "PT08.S1(CO)",
    "PT08.S2(NMHC)",
    "PT08.S3(NOx)",
    "PT08.S4(NO2)",
    "PT08.S5(O3)",
    "T",
    "RH",
    "AH",
}


def encode_measurement(measurement: dict) -> bytes:
    return (json.dumps(measurement) + "\n").encode("utf-8")


def validate_measurement(measurement: dict) -> dict:
    if not isinstance(measurement, dict):
        raise ValueError("Measurement must be a dictionary.")

    missing_fields = REQUIRED_FIELDS - set(measurement.keys())

    if missing_fields:
        raise ValueError(
            f"Missing measurement fields: {sorted(missing_fields)}"
        )

    for field in REQUIRED_FIELDS:
        value = measurement[field]

        if not isinstance(value, (int, float)):
            raise ValueError(
                f"Measurement field '{field}' must be numeric."
            )

    return validate_physical_ranges(measurement)


def decode_measurement(data: bytes) -> dict:
    text = data.decode("utf-8").strip()

    if not text:
        raise ValueError("Received empty serial message.")

    try:
        measurement = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError("Invalid JSON serial message.") from exc

    return validate_measurement(measurement)


def validate_physical_ranges(measurement: dict) -> dict:
    ranges = {
        "PT08.S1(CO)": (0, 5000),
        "PT08.S2(NMHC)": (0, 5000),
        "PT08.S3(NOx)": (0, 5000),
        "PT08.S4(NO2)": (0, 5000),
        "PT08.S5(O3)": (0, 5000),
        "T": (-40, 85),
        "RH": (0, 100),
        "AH": (0, 10),
    }

    for field, (minimum, maximum) in ranges.items():
        value = measurement[field]

        if value < minimum or value > maximum:
            raise ValueError(
                f"Measurement field '{field}' is outside "
                f"the allowed range [{minimum}, {maximum}]: {value}"
            )

    return measurement