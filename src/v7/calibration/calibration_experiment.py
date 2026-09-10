"""
V7.2 physics + ML calibration experiment.
"""

from dataclasses import dataclass

from src.v7.experiments.scenarios import Scenario

from .evaluation import (
    CalibrationEvaluation,
    evaluate_prediction,
)
from .model_adapter import CalibrationModelAdapter
from .sensor_array import (
    PhysicsSensorArray,
    SensorArrayMeasurement,
)


@dataclass(frozen=True)
class CalibrationExperimentResult:
    """Complete result of one physics + ML experiment."""

    scenario_id: str
    scenario_name: str

    measurement: SensorArrayMeasurement

    predicted_value: float
    reference_value: float

    evaluation: CalibrationEvaluation

    model_version: str
    target_variable: str

    provenance: str = (
        "V7.2 synthetic physics + existing V2 ML model"
    )

    def to_dict(self) -> dict:
        """Return complete experiment result."""

        return {
            "scenario_id": self.scenario_id,
            "scenario_name": self.scenario_name,
            "measurement": self.measurement.to_dict(),
            "predicted_value": self.predicted_value,
            "reference_value": self.reference_value,
            "evaluation": self.evaluation.to_dict(),
            "model_version": self.model_version,
            "target_variable": self.target_variable,
            "provenance": self.provenance,
        }


class CalibrationExperiment:
    """
    Run a complete physics-aware calibration experiment.

    Pipeline:

        Scenario
            ↓
        Physics sensor array
            ↓
        Eight model features
            ↓
        Existing V2 ML model
            ↓
        Synthetic reference
            ↓
        Error evaluation
    """

    def __init__(
        self,
        sensor_array: PhysicsSensorArray | None = None,
        model_adapter: CalibrationModelAdapter | None = None,
    ):
        self.sensor_array = (
            sensor_array
            or PhysicsSensorArray()
        )

        self.model_adapter = (
            model_adapter
            or CalibrationModelAdapter()
        )

    def run(
        self,
        scenario: Scenario,
        seed: int | None = 42,
    ) -> CalibrationExperimentResult:
        """Run one complete calibration experiment."""

        measurement = self.sensor_array.simulate(
            scenario=scenario,
            seed=seed,
        )

        model_input = measurement.to_model_input()

        prediction = self.model_adapter.predict(
            model_input
        )

        evaluation = evaluate_prediction(
            predicted_value=prediction,
            reference_value=scenario.true_value,
            unit=scenario.unit,
        )

        return CalibrationExperimentResult(
            scenario_id=scenario.scenario_id,
            scenario_name=scenario.name,
            measurement=measurement,
            predicted_value=prediction,
            reference_value=scenario.true_value,
            evaluation=evaluation,
            model_version=self.model_adapter.model_version,
            target_variable=self.model_adapter.target_variable,
        )