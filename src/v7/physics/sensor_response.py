"""
Physics-inspired sensor response model.

This is a simulation model, not a validated physical instrument model.
Its coefficients must be experimentally identified before being used
for real laboratory measurements.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class SensorParameters:
    sensitivity: float
    offset: float
    temperature_coefficient: float = 0.0
    humidity_coefficient: float = 0.0
    reference_temperature_c: float = 25.0
    reference_humidity_percent: float = 50.0


def sensor_response(
    true_value: float,
    temperature_c: float,
    relative_humidity_percent: float,
    parameters: SensorParameters,
) -> float:
    """
    Calculate idealized sensor response.
    """
    if true_value < 0:
        raise ValueError("True value cannot be negative.")

    if not 0 <= relative_humidity_percent <= 100:
        raise ValueError("Relative humidity must be between 0 and 100%.")

    temperature_effect = parameters.temperature_coefficient * (
        temperature_c - parameters.reference_temperature_c
    )

    humidity_effect = parameters.humidity_coefficient * (
        relative_humidity_percent - parameters.reference_humidity_percent
    )

    return (
        parameters.sensitivity * true_value
        + parameters.offset
        + temperature_effect
        + humidity_effect
    )