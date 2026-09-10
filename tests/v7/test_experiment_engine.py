import pytest

from src.v7.experiments import (
    ExperimentRunner,
    PhysicsSensorSimulator,
    get_scenario,
    list_scenarios,
)
from src.v7.physics import SensorParameters


def test_all_built_in_scenarios_exist():
    scenarios = list_scenarios()

    assert len(scenarios) == 10


def test_normal_lab_scenario():
    scenario = get_scenario("normal_lab")

    assert scenario.scenario_id == "normal_lab"
    assert scenario.true_value == pytest.approx(2.0)
    assert scenario.temperature_c == pytest.approx(25.0)
    assert scenario.relative_humidity_percent == pytest.approx(50.0)
    assert scenario.pressure_kpa == pytest.approx(101.325)


def test_unknown_scenario_rejected():
    with pytest.raises(ValueError):
        get_scenario("does_not_exist")


def test_simulator_produces_measurement():
    simulator = PhysicsSensorSimulator()

    measurement = simulator.simulate(
        get_scenario("normal_lab"),
        seed=42,
    )

    assert measurement.true_value == pytest.approx(2.0)
    assert measurement.unit == "mg/m³"
    assert measurement.provenance == "V7 synthetic physics simulation"


def test_simulation_is_reproducible():
    simulator = PhysicsSensorSimulator()

    first = simulator.simulate(
        get_scenario("normal_lab"),
        seed=42,
    )

    second = simulator.simulate(
        get_scenario("normal_lab"),
        seed=42,
    )

    assert first.sensor_value == pytest.approx(second.sensor_value)
    assert first.noise_component == pytest.approx(
        second.noise_component
    )


def test_temperature_changes_sensor_response():
    simulator = PhysicsSensorSimulator()

    normal = simulator.simulate(
        get_scenario("normal_lab"),
        seed=42,
    )

    hot = simulator.simulate(
        get_scenario("hot_environment"),
        seed=42,
    )

    assert hot.ideal_sensor_response != pytest.approx(
        normal.ideal_sensor_response
    )


def test_humidity_changes_sensor_response():
    simulator = PhysicsSensorSimulator()

    normal = simulator.simulate(
        get_scenario("normal_lab"),
        seed=42,
    )

    humid = simulator.simulate(
        get_scenario("high_humidity"),
        seed=42,
    )

    assert humid.ideal_sensor_response != pytest.approx(
        normal.ideal_sensor_response
    )


def test_drift_scenario_contains_drift():
    simulator = PhysicsSensorSimulator()

    measurement = simulator.simulate(
        get_scenario("sensor_drift"),
        seed=42,
    )

    assert measurement.drift_component == pytest.approx(0.35)


def test_high_noise_has_nonzero_noise():
    simulator = PhysicsSensorSimulator()

    measurement = simulator.simulate(
        get_scenario("high_noise"),
        seed=42,
    )

    assert measurement.noise_component != 0.0


def test_experiment_runner():
    runner = ExperimentRunner()

    result = runner.run(
        scenario_name="normal_lab",
        seed=42,
    )

    assert result.success is True
    assert result.scenario == "Normal Laboratory"
    assert result.measurement.true_value == pytest.approx(2.0)


def test_run_all_scenarios():
    runner = ExperimentRunner()

    results = runner.run_all(seed=42)

    assert len(results) == 10
    assert all(result.success for result in results)


def test_measurement_to_dict():
    runner = ExperimentRunner()

    result = runner.run(
        scenario_name="normal_lab",
        seed=42,
    )

    data = result.measurement.to_dict()

    assert "timestamp" in data
    assert "temperature_c" in data
    assert "relative_humidity_percent" in data
    assert "pressure_kpa" in data
    assert "sensor_value" in data
    assert "true_value" in data
    assert "provenance" in data


def test_custom_sensor_parameters():
    parameters = SensorParameters(
        sensitivity=2.0,
        offset=1.0,
    )

    simulator = PhysicsSensorSimulator(
        sensor_parameters=parameters,
    )

    measurement = simulator.simulate(
        get_scenario("normal_lab"),
        seed=42,
    )

    assert measurement.ideal_sensor_response == pytest.approx(5.0)


def test_scenario_has_stable_machine_identifier():
    scenarios = list_scenarios()

    scenario_ids = {
        scenario.scenario_id
        for scenario in scenarios
    }

    assert "normal_lab" in scenario_ids
    assert "hot_environment" in scenario_ids
    assert "sensor_drift" in scenario_ids

    assert len(scenario_ids) == len(scenarios)