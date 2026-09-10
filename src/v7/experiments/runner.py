"""
V7.1 experiment runner.
"""

from dataclasses import dataclass

from .measurement import Measurement
from .scenarios import get_scenario, list_scenarios
from .simulator import PhysicsSensorSimulator


@dataclass(frozen=True)
class ExperimentResult:
    """
    Result returned by a completed experiment.
    """

    scenario: str
    measurement: Measurement
    success: bool
    message: str


class ExperimentRunner:
    """
    Run reproducible physics experiments.
    """

    def __init__(
        self,
        simulator: PhysicsSensorSimulator | None = None,
    ):
        self.simulator = simulator or PhysicsSensorSimulator()

    def run(
        self,
        scenario_name: str,
        seed: int | None = 42,
    ) -> ExperimentResult:
        """
        Run one named experiment.
        """

        scenario = get_scenario(scenario_name)

        measurement = self.simulator.simulate(
            scenario=scenario,
            seed=seed,
        )

        return ExperimentResult(
            scenario=scenario.name,
            measurement=measurement,
            success=True,
            message="Synthetic physics experiment completed.",
        )

    def run_all(
        self,
        seed: int | None = 42,
    ) -> list[ExperimentResult]:
        """
        Run every registered scenario.
        """

        results = []

        for index, scenario in enumerate(list_scenarios()):
            scenario_seed = (
                None
                if seed is None
                else seed + index
            )

            result = self.run(
                scenario_name=scenario.scenario_id,
                seed=scenario_seed,
            )

            results.append(result)

        return results