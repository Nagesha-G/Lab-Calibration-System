import math

import pytest

from src.v7.physics import (
    ABSOLUTE_ZERO_C,
    R,
    SensorParameters,
    add_gaussian_noise,
    celsius_to_kelvin,
    first_order_step,
    fraction_to_ppm,
    kpa_to_pa,
    kelvin_to_celsius,
    linear_drift,
    mole_fractions,
    moles,
    pa_to_kpa,
    ppm_to_fraction,
    pressure,
    relative_humidity_to_vapor_pressure_hpa,
    saturation_vapor_pressure_hpa,
    sensor_response,
    total_pressure,
    volume,
)


def test_celsius_kelvin_conversion():
    assert celsius_to_kelvin(25.0) == pytest.approx(298.15)
    assert kelvin_to_celsius(298.15) == pytest.approx(25.0)


def test_temperature_below_absolute_zero_rejected():
    with pytest.raises(ValueError):
        celsius_to_kelvin(ABSOLUTE_ZERO_C - 0.1)


def test_pressure_unit_conversion():
    assert kpa_to_pa(101.325) == pytest.approx(101325.0)
    assert pa_to_kpa(101325.0) == pytest.approx(101.325)


def test_ppm_conversion():
    assert ppm_to_fraction(1000.0) == pytest.approx(0.001)
    assert fraction_to_ppm(0.001) == pytest.approx(1000.0)


def test_ideal_gas_law_pressure():
    result = pressure(
        moles=1.0,
        temperature_c=25.0,
        volume_m3=1.0,
    )

    expected = R * 298.15

    assert result == pytest.approx(expected)


def test_ideal_gas_law_round_trip():
    original_moles = 0.5
    temperature_c = 25.0
    volume_m3 = 0.02

    calculated_pressure = pressure(
        original_moles,
        temperature_c,
        volume_m3,
    )

    calculated_moles = moles(
        calculated_pressure,
        temperature_c,
        volume_m3,
    )

    assert calculated_moles == pytest.approx(original_moles)


def test_ideal_gas_volume():
    calculated_pressure = 101325.0
    calculated_moles = 1.0

    calculated_volume = volume(
        calculated_moles,
        25.0,
        calculated_pressure,
    )

    expected = (
        calculated_moles * R * 298.15
    ) / calculated_pressure

    assert calculated_volume == pytest.approx(expected)


def test_humidity_at_50_percent():
    saturation = saturation_vapor_pressure_hpa(25.0)

    vapor_pressure = relative_humidity_to_vapor_pressure_hpa(
        25.0,
        50.0,
    )

    assert vapor_pressure == pytest.approx(
        saturation * 0.5
    )


def test_gas_mixture():
    partial_pressures = {
        "CO": 10_000.0,
        "N2": 70_000.0,
        "O2": 20_000.0,
    }

    assert total_pressure(partial_pressures) == pytest.approx(100_000.0)

    fractions = mole_fractions(partial_pressures)

    assert fractions["CO"] == pytest.approx(0.10)
    assert fractions["N2"] == pytest.approx(0.70)
    assert fractions["O2"] == pytest.approx(0.20)

    assert sum(fractions.values()) == pytest.approx(1.0)


def test_sensor_response_without_environmental_effects():
    parameters = SensorParameters(
        sensitivity=2.0,
        offset=0.5,
    )

    result = sensor_response(
        true_value=3.0,
        temperature_c=25.0,
        relative_humidity_percent=50.0,
        parameters=parameters,
    )

    assert result == pytest.approx(6.5)


def test_sensor_environmental_effects():
    parameters = SensorParameters(
        sensitivity=2.0,
        offset=0.5,
        temperature_coefficient=0.1,
        humidity_coefficient=0.02,
    )

    result = sensor_response(
        true_value=3.0,
        temperature_c=35.0,
        relative_humidity_percent=70.0,
        parameters=parameters,
    )

    expected = (
        2.0 * 3.0
        + 0.5
        + 0.1 * 10.0
        + 0.02 * 20.0
    )

    assert result == pytest.approx(expected)


def test_noise_is_reproducible_with_seed():
    first = add_gaussian_noise(
        value=10.0,
        standard_deviation=0.5,
        seed=42,
    )

    second = add_gaussian_noise(
        value=10.0,
        standard_deviation=0.5,
        seed=42,
    )

    assert first == second


def test_linear_drift():
    result = linear_drift(
        initial_bias=0.0,
        drift_rate_per_day=0.01,
        elapsed_days=30,
    )

    assert result == pytest.approx(0.3)


def test_first_order_sensor_response():
    result = first_order_step(
        current_value=0.0,
        target_value=10.0,
        time_step_seconds=1.0,
        time_constant_seconds=10.0,
    )

    assert result == pytest.approx(1.0)