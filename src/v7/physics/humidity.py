"""
Humidity and water-vapor calculations.

The implementation uses the Magnus approximation for saturation
vapor pressure over liquid water.
"""

import math


def saturation_vapor_pressure_hpa(temperature_c: float) -> float:
    """
    Calculate saturation vapor pressure in hPa.

    Magnus approximation.
    """
    if temperature_c < -45 or temperature_c > 60:
        raise ValueError(
            "Temperature outside the supported Magnus approximation range."
        )

    return 6.112 * math.exp(
        (17.62 * temperature_c) / (243.12 + temperature_c)
    )


def relative_humidity_to_vapor_pressure_hpa(
    temperature_c: float,
    relative_humidity_percent: float,
) -> float:
    """
    Convert relative humidity to actual water-vapor pressure.
    """
    if not 0 <= relative_humidity_percent <= 100:
        raise ValueError("Relative humidity must be between 0 and 100%.")

    saturation = saturation_vapor_pressure_hpa(temperature_c)

    return saturation * (relative_humidity_percent / 100.0)


def vapor_pressure_to_relative_humidity_percent(
    temperature_c: float,
    vapor_pressure_hpa: float,
) -> float:
    """Convert vapor pressure to relative humidity."""
    if vapor_pressure_hpa < 0:
        raise ValueError("Vapor pressure cannot be negative.")

    saturation = saturation_vapor_pressure_hpa(temperature_c)

    relative_humidity = (vapor_pressure_hpa / saturation) * 100.0

    return relative_humidity