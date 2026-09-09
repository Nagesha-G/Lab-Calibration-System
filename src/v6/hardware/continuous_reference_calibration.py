import time

from src.v6.hardware.calibration_pair import CalibrationPair
from src.v6.hardware.reference_calibration import run_reference_calibration


def run_continuous_reference_calibration(
    pair: CalibrationPair,
    instrument_id: int,
    model_id: int,
    interval_seconds: float = 1.0,
    number_of_cycles: int = 5,
):
    if interval_seconds <= 0:
        raise ValueError("Interval must be greater than 0.")

    if number_of_cycles <= 0:
        raise ValueError("Number of cycles must be greater than 0.")

    if not pair.is_ready():
        raise RuntimeError(
            "Instrument and reference standard must be connected."
        )

    results = []

    for cycle in range(number_of_cycles):
        try:
            calibration = run_reference_calibration(
                pair=pair,
                instrument_id=instrument_id,
                model_id=model_id,
            )

            results.append(calibration)

            print(
                f"Cycle {cycle + 1} | "
                f"Record ID: {calibration.record_id} | "
                f"Estimated: {calibration.estimated_value:.4f} | "
                f"Reference: {calibration.reference_value:.4f} | "
                f"Status: {calibration.status}"
            )

        except Exception as exc:
            print(
                f"Cycle {cycle + 1} | "
                f"ERROR: {exc}"
            )

        if cycle < number_of_cycles - 1:
            time.sleep(interval_seconds)

    return results