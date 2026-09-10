"""
V7.1 Physics-aware sensor simulator.

This module combines the V7 physics primitives into a complete
synthetic measurement pipeline.
"""

from datetime import datetime

from src.v7.physics import (
    SensorParameters,
    add_gaussian_noise,
    apply_drift,
    sensor_response,
)

from .measurement import Measurement
from .scenarios import Scenario


class PhysicsSensorSimulator:
    """
    Simulate a sensor operating under a physical scenario.

    The coefficients used here are deliberately explicit simulation
    parameters. They are not claimed to represent a particular
    commercial sensor.
    """

    def __init__(
        self,
        sensor_parameters: SensorParameters | None = None,
    ):
        self.sensor_parameters = sensor_parameters or SensorParameters(
            sensitivity=1.0,
            offset=0.0,
            temperature_coefficient=0.01,
            humidity_coefficient=0.002,
            reference_temperature_c=25.0,
            reference_humidity_percent=50.0,
        )

    def simulate(
        self,
        scenario: Scenario,
        seed: int | None = 42,
    ) -> Measurement:
        """Run one synthetic measurement."""

        ideal_response = sensor_response(
            true_value=scenario.true_value,
            temperature_c=scenario.temperature_c,
            relative_humidity_percent=scenario.relative_humidity_percent,
            parameters=self.sensor_parameters,
        )

        drifted_response = apply_drift(
            measurement=ideal_response,
            initial_bias=scenario.initial_bias,
            drift_rate_per_day=scenario.drift_rate_per_day,
            elapsed_days=scenario.elapsed_days,
        )

        drift_component = drifted_response - ideal_response

        sensor_value = add_gaussian_noise(
            value=drifted_response,
            standard_deviation=scenario.noise_std,
            seed=seed,
        )

        noise_component = sensor_value - drifted_response

        return Measurement(
            timestamp=datetime.now(),
            scenario=scenario.name,
            true_value=scenario.true_value,
            sensor_value=sensor_value,
            temperature_c=scenario.temperature_c,
            relative_humidity_percent=scenario.relative_humidity_percent,
            pressure_kpa=scenario.pressure_kpa,
            ideal_sensor_response=ideal_response,
            noise_component=noise_component,
            drift_component=drift_component,
            unit=scenario.unit,
        )