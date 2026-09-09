import time

from src.v6.hardware.instrument_interface import InstrumentInterface
from src.v6.hardware.calibration_bridge import acquire_and_calibrate


def run_continuous_calibration(
    instrument: InstrumentInterface,
    instrument_id: int,
    model_id: int,
    reference_value: float,
    interval_seconds: float = 2.0,
    number_of_cycles: int = 5,
):
    if interval_seconds <= 0:
        raise ValueError("Interval must be greater than 0.")

    if number_of_cycles <= 0:
        raise ValueError("Number of cycles must be greater than 0.")

    if not instrument.is_connected():
        raise RuntimeError("Instrument is not connected.")

    results = []

    for _ in range(number_of_cycles):
        calibration = acquire_and_calibrate(
            instrument=instrument,
            instrument_id=instrument_id,
            model_id=model_id,
            reference_value=reference_value,
        )

        results.append(calibration)

        print(
            f"Record {calibration.record_id} | "
            f"Estimated: {calibration.estimated_value:.4f} | "
            f"Reference: {calibration.reference_value:.4f} | "
            f"Status: {calibration.status}"
        )

        time.sleep(interval_seconds)

    return results