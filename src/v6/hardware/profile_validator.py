from src.v6.hardware.instrument_profile import InstrumentProfile


def validate_profile_measurement(
    profile: InstrumentProfile,
    measurement: dict,
) -> dict:
    profile.validate()

    if not isinstance(measurement, dict):
        raise ValueError("Measurement must be a dictionary.")

    expected_fields = {
        field.name
        for field in profile.measurement_fields
    }

    missing_fields = expected_fields - set(measurement.keys())

    if missing_fields:
        raise ValueError(
            f"Missing measurement fields: {sorted(missing_fields)}"
        )

    for field in profile.measurement_fields:
        value = measurement[field.name]

        if not isinstance(value, (int, float)):
            raise ValueError(
                f"Measurement field '{field.name}' must be numeric."
            )

        if value < field.minimum or value > field.maximum:
            raise ValueError(
                f"Measurement field '{field.name}' is outside "
                f"the allowed range "
                f"[{field.minimum}, {field.maximum}]: {value}"
            )

    return measurement