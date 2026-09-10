"""
Structured measurement result for the V7 experiment engine.
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Measurement:
    """
    A simulated instrument measurement.

    `true_value` exists only because this is a simulation. A physical
    instrument does not have access to the true value.
    """

    timestamp: datetime
    scenario: str

    true_value: float
    sensor_value: float

    temperature_c: float
    relative_humidity_percent: float
    pressure_kpa: float

    ideal_sensor_response: float
    noise_component: float
    drift_component: float

    unit: str
    provenance: str = "V7 synthetic physics simulation"

    @property
    def absolute_error_from_truth(self) -> float:
        """Calculate absolute simulation error."""
        return abs(self.sensor_value - self.true_value)

    @property
    def error_from_truth(self) -> float:
        """Calculate signed simulation error."""
        return self.sensor_value - self.true_value

    def to_dict(self) -> dict:
        """Convert measurement to a serializable dictionary."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "scenario": self.scenario,
            "true_value": self.true_value,
            "sensor_value": self.sensor_value,
            "temperature_c": self.temperature_c,
            "relative_humidity_percent": self.relative_humidity_percent,
            "pressure_kpa": self.pressure_kpa,
            "ideal_sensor_response": self.ideal_sensor_response,
            "noise_component": self.noise_component,
            "drift_component": self.drift_component,
            "unit": self.unit,
            "provenance": self.provenance,
            "error_from_truth": self.error_from_truth,
            "absolute_error_from_truth": self.absolute_error_from_truth,
        }