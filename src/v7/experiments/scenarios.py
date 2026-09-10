"""
V7.1 Built-in physical experiment scenarios.

These scenarios are synthetic demonstrations. They are not measurements
from a physical laboratory instrument.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Scenario:
    """
    Definition of a reproducible physical experiment scenario.

    scenario_id:
        Stable machine/API identifier.

    name:
        Human-readable scenario name.

    true_value:
        Synthetic ground-truth measurand. This exists only inside
        the simulation and must never be interpreted as a physical
        instrument measurement.
    """

    scenario_id: str
    name: str
    description: str
    true_value: float
    temperature_c: float
    relative_humidity_percent: float
    pressure_kpa: float
    noise_std: float
    initial_bias: float
    drift_rate_per_day: float
    elapsed_days: float
    unit: str = "mg/m³"


SCENARIOS = {
    "normal_lab": Scenario(
        scenario_id="normal_lab",
        name="Normal Laboratory",
        description="Stable laboratory conditions with a low-noise sensor.",
        true_value=2.0,
        temperature_c=25.0,
        relative_humidity_percent=50.0,
        pressure_kpa=101.325,
        noise_std=0.02,
        initial_bias=0.0,
        drift_rate_per_day=0.0,
        elapsed_days=0.0,
    ),

    "hot_environment": Scenario(
        scenario_id="hot_environment",
        name="Hot Environment",
        description="Elevated temperature demonstrating thermal sensor influence.",
        true_value=2.0,
        temperature_c=38.0,
        relative_humidity_percent=42.0,
        pressure_kpa=100.8,
        noise_std=0.02,
        initial_bias=0.0,
        drift_rate_per_day=0.0,
        elapsed_days=0.0,
    ),

    "cold_environment": Scenario(
        scenario_id="cold_environment",
        name="Cold Environment",
        description="Lower temperature demonstrating thermal sensor influence.",
        true_value=2.0,
        temperature_c=8.0,
        relative_humidity_percent=55.0,
        pressure_kpa=102.0,
        noise_std=0.02,
        initial_bias=0.0,
        drift_rate_per_day=0.0,
        elapsed_days=0.0,
    ),

    "high_humidity": Scenario(
        scenario_id="high_humidity",
        name="High Humidity",
        description="High relative humidity demonstrating environmental influence.",
        true_value=2.0,
        temperature_c=25.0,
        relative_humidity_percent=85.0,
        pressure_kpa=101.325,
        noise_std=0.02,
        initial_bias=0.0,
        drift_rate_per_day=0.0,
        elapsed_days=0.0,
    ),

    "low_humidity": Scenario(
        scenario_id="low_humidity",
        name="Low Humidity",
        description="Dry environmental conditions.",
        true_value=2.0,
        temperature_c=25.0,
        relative_humidity_percent=20.0,
        pressure_kpa=101.325,
        noise_std=0.02,
        initial_bias=0.0,
        drift_rate_per_day=0.0,
        elapsed_days=0.0,
    ),

    "sensor_drift": Scenario(
        scenario_id="sensor_drift",
        name="Sensor Drift",
        description="Aging sensor with gradually increasing measurement bias.",
        true_value=2.0,
        temperature_c=25.0,
        relative_humidity_percent=50.0,
        pressure_kpa=101.325,
        noise_std=0.02,
        initial_bias=0.05,
        drift_rate_per_day=0.01,
        elapsed_days=30.0,
    ),

    "high_noise": Scenario(
        scenario_id="high_noise",
        name="High Noise",
        description="Noisy measurement environment.",
        true_value=2.0,
        temperature_c=25.0,
        relative_humidity_percent=50.0,
        pressure_kpa=101.325,
        noise_std=0.30,
        initial_bias=0.0,
        drift_rate_per_day=0.0,
        elapsed_days=0.0,
    ),

    "concentration_step": Scenario(
        scenario_id="concentration_step",
        name="Concentration Step",
        description="A sudden change in the target concentration.",
        true_value=5.0,
        temperature_c=25.0,
        relative_humidity_percent=50.0,
        pressure_kpa=101.325,
        noise_std=0.02,
        initial_bias=0.0,
        drift_rate_per_day=0.0,
        elapsed_days=0.0,
    ),

    "faulty_sensor": Scenario(
        scenario_id="faulty_sensor",
        name="Faulty Sensor",
        description="Sensor with a significant fixed measurement bias.",
        true_value=2.0,
        temperature_c=25.0,
        relative_humidity_percent=50.0,
        pressure_kpa=101.325,
        noise_std=0.02,
        initial_bias=0.75,
        drift_rate_per_day=0.0,
        elapsed_days=0.0,
    ),

    "combined_stress": Scenario(
        scenario_id="combined_stress",
        name="Combined Environmental Stress",
        description=(
            "Temperature, humidity, noise and drift acting together."
        ),
        true_value=3.0,
        temperature_c=35.0,
        relative_humidity_percent=80.0,
        pressure_kpa=99.5,
        noise_std=0.15,
        initial_bias=0.05,
        drift_rate_per_day=0.01,
        elapsed_days=20.0,
    ),
}


def get_scenario(name: str) -> Scenario:
    """
    Return a scenario using its stable machine identifier.
    """
    try:
        return SCENARIOS[name]
    except KeyError:
        available = ", ".join(sorted(SCENARIOS))

        raise ValueError(
            f"Unknown scenario '{name}'. "
            f"Available scenarios: {available}"
        )


def list_scenarios() -> list[Scenario]:
    """
    Return all registered scenarios.
    """
    return list(SCENARIOS.values())