import pytest

from src.v7.calibration import (
    CalibrationExperiment,
    CalibrationModelAdapter,
    PhysicsSensorArray,
    evaluate_prediction,
    mean_absolute_error,
    root_mean_squared_error,
)

from src.v7.experiments import get_scenario


def test_sensor_array_has_eight_model_features():
    array = PhysicsSensorArray()

    measurement = array.simulate(
        get_scenario("normal_lab"),
        seed=42,
    )

    model_input = measurement.to_model_input()

    expected_features = {
        "PT08.S1(CO)",
        "PT08.S2(NMHC)",
        "PT08.S3(NOx)",
        "PT08.S4(NO2)",
        "PT08.S5(O3)",
        "T",
        "RH",
        "AH",
    }

    assert set(model_input.keys()) == expected_features


def test_absolute_humidity_is_positive():
    array = PhysicsSensorArray()

    measurement = array.simulate(
        get_scenario("normal_lab"),
        seed=42,
    )

    assert measurement.absolute_humidity_g_m3 > 0


def test_absolute_humidity_changes_with_temperature():
    array = PhysicsSensorArray()

    cold = array.simulate(
        get_scenario("cold_environment"),
        seed=42,
    )

    hot = array.simulate(
        get_scenario("hot_environment"),
        seed=42,
    )

    assert (
        cold.absolute_humidity_g_m3
        != pytest.approx(
            hot.absolute_humidity_g_m3
        )
    )


def test_sensor_array_reproducible():
    array = PhysicsSensorArray()

    first = array.simulate(
        get_scenario("normal_lab"),
        seed=42,
    )

    second = array.simulate(
        get_scenario("normal_lab"),
        seed=42,
    )

    assert first.pt08_s1_co == pytest.approx(
        second.pt08_s1_co
    )

    assert first.pt08_s5_o3 == pytest.approx(
        second.pt08_s5_o3
    )


def test_model_adapter_loads_v2_model():
    adapter = CalibrationModelAdapter()

    assert adapter.model is not None
    assert adapter.model_version == "v2.0.0"
    assert adapter.target_variable == "CO(GT)"


def test_model_adapter_prediction():
    array = PhysicsSensorArray()
    adapter = CalibrationModelAdapter()

    measurement = array.simulate(
        get_scenario("normal_lab"),
        seed=42,
    )

    prediction = adapter.predict(
        measurement.to_model_input()
    )

    assert isinstance(prediction, float)


def test_model_adapter_rejects_missing_feature():
    adapter = CalibrationModelAdapter()

    with pytest.raises(ValueError):
        adapter.predict(
            {
                "T": 25.0,
            }
        )


def test_prediction_evaluation():
    result = evaluate_prediction(
        predicted_value=2.2,
        reference_value=2.0,
    )

    assert result.error == pytest.approx(0.2)
    assert result.absolute_error == pytest.approx(0.2)


def test_mae():
    predictions = [1.0, 2.0, 3.0]
    references = [1.1, 1.8, 3.2]

    result = mean_absolute_error(
        predictions,
        references,
    )

    assert result == pytest.approx(
        (0.1 + 0.2 + 0.2) / 3
    )


def test_rmse():
    predictions = [1.0, 2.0, 3.0]
    references = [1.1, 1.8, 3.2]

    result = root_mean_squared_error(
        predictions,
        references,
    )

    expected = (
        (
            0.1**2
            + 0.2**2
            + 0.2**2
        ) / 3
    ) ** 0.5

    assert result == pytest.approx(expected)


def test_complete_calibration_experiment():
    experiment = CalibrationExperiment()

    result = experiment.run(
        get_scenario("normal_lab"),
        seed=42,
    )

    assert result.scenario_id == "normal_lab"
    assert result.scenario_name == "Normal Laboratory"
    assert result.reference_value == pytest.approx(2.0)
    assert isinstance(result.predicted_value, float)
    assert result.model_version == "v2.0.0"
    assert result.target_variable == "CO(GT)"


def test_complete_experiment_serialization():
    experiment = CalibrationExperiment()

    result = experiment.run(
        get_scenario("hot_environment"),
        seed=42,
    )

    data = result.to_dict()

    assert data["scenario_id"] == "hot_environment"
    assert "measurement" in data
    assert "predicted_value" in data
    assert "reference_value" in data
    assert "evaluation" in data


def test_scenario_environment_reaches_model_features():
    experiment = CalibrationExperiment()

    result = experiment.run(
        get_scenario("high_humidity"),
        seed=42,
    )

    model_input = result.measurement.to_model_input()

    assert model_input["RH"] == pytest.approx(85.0)
    assert model_input["T"] == pytest.approx(25.0)
    assert model_input["AH"] > 0