"""
Basic unit conversions used by the V7 physics engine.
"""

from .constants import ABSOLUTE_ZERO_C


def celsius_to_kelvin(celsius: float) -> float:
    """
    Convert Celsius to Kelvin.

    Temperatures below absolute zero are physically invalid.
    """
    if celsius < ABSOLUTE_ZERO_C:
        raise ValueError(
            "Temperature cannot be below absolute zero."
        )

    return celsius + 273.15


def kelvin_to_celsius(kelvin: float) -> float:
    """
    Convert Kelvin to Celsius.

    Negative Kelvin temperatures are not accepted by this
    thermodynamic model.
    """
    if kelvin < 0:
        raise ValueError(
            "Kelvin temperature cannot be negative."
        )

    return kelvin - 273.15


def kpa_to_pa(kpa: float) -> float:
    """Convert kilopascals to pascals."""
    return kpa * 1000.0


def pa_to_kpa(pa: float) -> float:
    """Convert pascals to kilopascals."""
    return pa / 1000.0


def ppm_to_fraction(ppm: float) -> float:
    """Convert parts per million to a dimensionless fraction."""
    if ppm < 0:
        raise ValueError("PPM cannot be negative.")

    return ppm / 1_000_000.0


def fraction_to_ppm(fraction: float) -> float:
    """Convert a dimensionless fraction to parts per million."""
    if fraction < 0:
        raise ValueError("Fraction cannot be negative.")

    return fraction * 1_000_000.0