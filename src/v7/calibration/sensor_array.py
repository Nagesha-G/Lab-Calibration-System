"""
V7.2 Physics-aware multi-sensor array.

The sensor channels are designed to match the feature structure
used by the V2 CO calibration model.

Important:
The sensor-response coefficients in this module are synthetic
simulation parameters. They are NOT experimentally calibrated
commercial-sensor coefficients.
"""

from dataclasses import dataclass

from src.v7.experiments.scenarios import Scenario
from src.v7.physics import (
    SensorParameters,
    add_gaussian_noise,
    apply_drift,
    relative_humidity_to_vapor_pressure_hpa,
    sensor_response,
)


@dataclass(frozen=True)
class SensorArrayMeasurement:
    """
    Eight-channel measurement compatible with the V2 model.

    Channels:
        PT08.S1(CO)
        PT08.S2(NMHC)
        PT08.S3(NOx)
        PT08.S4(NO2)
        PT08.S5(O3)
        T
        RH
        AH
    """

    pt08_s1_co: float
    pt08_s2_nmhc: float
    pt08_s3_nox: float
    pt08_s4_no2: float
    pt08_s5_o3: float

    temperature_c: float
    relative_humidity_percent: float
    absolute_humidity_g_m3: float

    unit: str = "synthetic sensor response"
    provenance: str = "V7.2 synthetic physics sensor array"

    def to_model_input(self) -> dict[str, float]:
        """
        Return features using the exact V2 model column names.
        """

        return {
            "PT08.S1(CO)": self.pt08_s1_co,
            "PT08.S2(NMHC)": self.pt08_s2_nmhc,
            "PT08.S3(NOx)": self.pt08_s3_nox,
            "PT08.S4(NO2)": self.pt08_s4_no2,
            "PT08.S5(O3)": self.pt08_s5_o3,
            "T": self.temperature_c,
            "RH": self.relative_humidity_percent,
            "AH": self.absolute_humidity_g_m3,
        }

    def to_dict(self) -> dict[str, float | str]:
        """Return a serializable representation."""

        return {
            **self.to_model_input(),
            "unit": self.unit,
            "provenance": self.provenance,
        }


class PhysicsSensorArray:
    """
    Simulate the five gas-sensor channels plus environmental channels.

    Each gas channel has its own sensitivity and environmental response.
    """

    def __init__(self):
        self.sensor_parameters = {
            "PT08.S1(CO)": SensorParameters(
                sensitivity=100.0,
                offset=700.0,
                temperature_coefficient=1.5,
                humidity_coefficient=0.5,
            ),
            "PT08.S2(NMHC)": SensorParameters(
                sensitivity=120.0,
                offset=500.0,
                temperature_coefficient=1.0,
                humidity_coefficient=0.4,
            ),
            "PT08.S3(NOx)": SensorParameters(
                sensitivity=80.0,
                offset=900.0,
                temperature_coefficient=-1.0,
                humidity_coefficient=0.3,
            ),
            "PT08.S4(NO2)": SensorParameters(
                sensitivity=90.0,
                offset=600.0,
                temperature_coefficient=1.2,
                humidity_coefficient=0.4,
            ),
            "PT08.S5(O3)": SensorParameters(
                sensitivity=110.0,
                offset=400.0,
                temperature_coefficient=0.8,
                humidity_coefficient=0.6,
            ),
        }

    def _simulate_channel(
        self,
        true_value: float,
        temperature_c: float,
        relative_humidity_percent: float,
        parameters: SensorParameters,
        noise_std: float,
        initial_bias: float,
        drift_rate_per_day: float,
        elapsed_days: float,
        seed: int | None,
    ) -> float:
        """Simulate one sensor channel."""

        response = sensor_response(
            true_value=true_value,
            temperature_c=temperature_c,
            relative_humidity_percent=relative_humidity_percent,
            parameters=parameters,
        )

        response_with_drift = apply_drift(
            measurement=response,
            initial_bias=initial_bias,
            drift_rate_per_day=drift_rate_per_day,
            elapsed_days=elapsed_days,
        )

        return add_gaussian_noise(
            value=response_with_drift,
            standard_deviation=noise_std,
            seed=seed,
        )

    @staticmethod
    def calculate_absolute_humidity_g_m3(
        temperature_c: float,
        relative_humidity_percent: float,
        pressure_kpa: float,
    ) -> float:
        """
        Calculate approximate absolute humidity in g/m³.

        The calculation derives water-vapor partial pressure from
        temperature and relative humidity and then applies the
        ideal-gas relationship to water vapor.

        Molar mass of water:
            18.01528 g/mol
        """

        if pressure_kpa <= 0:
            raise ValueError(
                "Pressure must be greater than zero."
            )

        vapor_pressure_hpa = (
            relative_humidity_to_vapor_pressure_hpa(
                temperature_c=temperature_c,
                relative_humidity_percent=relative_humidity_percent,
            )
        )

        vapor_pressure_pa = vapor_pressure_hpa * 100.0

        temperature_k = temperature_c + 273.15

        water_molar_mass_g_mol = 18.01528

        # Ideal gas law:
        #
        # PV = nRT
        #
        # n/V = P/(RT)
        #
        # mass/V = P*M/(RT)
        #
        # Convert kg/m³ to g/m³ by multiplying by 1000.
        universal_gas_constant = 8.31446261815324

        concentration_kg_m3 = (
            vapor_pressure_pa
            * (water_molar_mass_g_mol / 1000.0)
            / (
                universal_gas_constant
                * temperature_k
            )
        )

        return concentration_kg_m3 * 1000.0

    def simulate(
        self,
        scenario: Scenario,
        seed: int | None = 42,
    ) -> SensorArrayMeasurement:
        """
        Generate a complete eight-channel sensor measurement.
        """

        seeds = (
            [None] * 5
            if seed is None
            else [seed + index for index in range(5)]
        )

        values = {}

        for index, (channel, parameters) in enumerate(
            self.sensor_parameters.items()
        ):
            values[channel] = self._simulate_channel(
                true_value=scenario.true_value,
                temperature_c=scenario.temperature_c,
                relative_humidity_percent=(
                    scenario.relative_humidity_percent
                ),
                parameters=parameters,
                noise_std=scenario.noise_std,
                initial_bias=scenario.initial_bias,
                drift_rate_per_day=scenario.drift_rate_per_day,
                elapsed_days=scenario.elapsed_days,
                seed=seeds[index],
            )

        absolute_humidity = self.calculate_absolute_humidity_g_m3(
            temperature_c=scenario.temperature_c,
            relative_humidity_percent=(
                scenario.relative_humidity_percent
            ),
            pressure_kpa=scenario.pressure_kpa,
        )

        return SensorArrayMeasurement(
            pt08_s1_co=values["PT08.S1(CO)"],
            pt08_s2_nmhc=values["PT08.S2(NMHC)"],
            pt08_s3_nox=values["PT08.S3(NOx)"],
            pt08_s4_no2=values["PT08.S4(NO2)"],
            pt08_s5_o3=values["PT08.S5(O3)"],
            temperature_c=scenario.temperature_c,
            relative_humidity_percent=(
                scenario.relative_humidity_percent
            ),
            absolute_humidity_g_m3=absolute_humidity,
        )