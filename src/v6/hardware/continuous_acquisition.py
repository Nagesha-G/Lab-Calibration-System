import time

from src.v6.hardware.acquisition_service import AcquisitionService


def run_acquisition(
    service: AcquisitionService,
    interval_seconds: float = 1.0,
    number_of_cycles: int = 5,
):
    if interval_seconds <= 0:
        raise ValueError("Interval must be greater than 0.")

    if number_of_cycles <= 0:
        raise ValueError("Number of cycles must be greater than 0.")

    results = []
    errors = []

    for cycle in range(number_of_cycles):
        try:
            measurement = service.acquire_once()
            results.append(measurement)

            print(
                f"Cycle {cycle + 1} | "
                f"Measurement ID: {measurement.measurement_id}"
            )

        except Exception as exc:
            errors.append(
                {
                    "cycle": cycle + 1,
                    "error": str(exc),
                }
            )

            print(
                f"Cycle {cycle + 1} | "
                f"ERROR: {exc}"
            )

        if cycle < number_of_cycles - 1:
            time.sleep(interval_seconds)

    return {
        "measurements": results,
        "errors": errors,
    }