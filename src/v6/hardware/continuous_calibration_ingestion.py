import time

from src.v6.hardware.calibration_ingestion import (
    CalibrationIngestionService,
)


def run_calibration_ingestion(
    service: CalibrationIngestionService,
    interval_seconds: float = 1.0,
    number_of_cycles: int = 5,
):
    if interval_seconds <= 0:
        raise ValueError("Interval must be greater than 0.")

    if number_of_cycles <= 0:
        raise ValueError("Number of cycles must be greater than 0.")

    results = []

    for cycle in range(number_of_cycles):
        try:
            calibration = service.calibrate_once()
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