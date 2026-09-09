from src.v5.services.calibration_engine import run_calibration
from src.v6.hardware.calibration_pair import CalibrationPair
from src.v6.hardware.v5_bridge import acquire_and_store_measurement


def run_reference_calibration(
    pair: CalibrationPair,
    instrument_id: int,
    model_id: int,
):
    if not pair.is_ready():
        raise RuntimeError(
            "Instrument and reference standard must be connected."
        )

    reference_value = pair.reference.read_reference_value()

    measurement_data = pair.instrument.read_measurement()

    measurement = acquire_and_store_measurement(
        instrument=pair.instrument,
        instrument_id=instrument_id,
    )

    calibration = run_calibration(
        instrument_id=instrument_id,
        measurement_id=measurement.measurement_id,
        model_id=model_id,
        reference_value=reference_value,
    )

    return calibration