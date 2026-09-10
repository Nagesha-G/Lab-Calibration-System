"""
Temperature-related physical calculations.
"""

from .constants import ABSOLUTE_ZERO_C
from .units import celsius_to_kelvin


def validate_celsius(celsius: float) -> None:
    """Reject temperatures below absolute zero."""
    if celsius < ABSOLUTE_ZERO_C:
        raise ValueError("Temperature cannot be below absolute zero.")


def to_kelvin(celsius: float) -> float:
    """Validate and convert Celsius to Kelvin."""
    validate_celsius(celsius)
    return celsius_to_kelvin(celsius)


def temperature_difference(
    temperature_1_c: float,
    temperature_2_c: float,
) -> float:
    """Return temperature difference in Celsius."""
    validate_celsius(temperature_1_c)
    validate_celsius(temperature_2_c)

    return temperature_1_c - temperature_2_c