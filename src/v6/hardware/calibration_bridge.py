from src.v5.services.calibration_engine import run_calibration
from src.v6.hardware.instrument_interface import InstrumentInterface
from src.v6.hardware.v5_bridge import acquire_and_store_measurement


def acquire_and_calibrate(
    instrument: InstrumentInterface,
    instrument_id: int,
    model_id: int,
    reference_value: float,
):
    measurement = acquire_and_store_measurement(
        instrument=instrument,
        instrument_id=instrument_id,
    )

    calibration = run_calibration(
        instrument_id=instrument_id,
        measurement_id=measurement.measurement_id,
        model_id=model_id,
        reference_value=reference_value,
    )

    return calibration