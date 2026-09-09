from src.v6.hardware.reference_standard import ReferenceStandard


def validate_reference_value(
    reference: ReferenceStandard,
    minimum: float = 0.01,
    maximum: float = 20.0,
) -> float:
    if not reference.is_connected():
        raise RuntimeError(
            "Reference standard is not connected."
        )

    if minimum < 0:
        raise ValueError("Minimum cannot be negative.")

    if maximum <= minimum:
        raise ValueError(
            "Maximum must be greater than minimum."
        )

    value = reference.read_reference_value()

    if value < minimum or value > maximum:
        raise ValueError(
            f"Reference value {value} is outside "
            f"the allowed range [{minimum}, {maximum}]."
        )

    return value