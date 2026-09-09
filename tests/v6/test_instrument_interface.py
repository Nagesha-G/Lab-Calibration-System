from src.v6.hardware.simulator.simulated_instrument import SimulatedInstrument
from src.v6.hardware.measurement_runner import MeasurementRunner


def test_simulated_instrument_works_with_measurement_runner():
    instrument = SimulatedInstrument(1)

    instrument.connect()

    runner = MeasurementRunner(instrument)

    measurement = runner.collect()

    instrument.disconnect()

    assert isinstance(measurement, dict)

    required_fields = {
        "PT08.S1(CO)",
        "PT08.S2(NMHC)",
        "PT08.S3(NOx)",
        "PT08.S4(NO2)",
        "PT08.S5(O3)",
        "T",
        "RH",
        "AH",
    }

    assert required_fields.issubset(measurement.keys())