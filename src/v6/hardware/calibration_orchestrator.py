import time

from src.v6.hardware.hardware_in_loop import HardwareInLoopController


class CalibrationOrchestrator:
    """
    Coordinates repeated hardware calibration cycles.
    """

    def __init__(
        self,
        controller: HardwareInLoopController,
    ):
        self.controller = controller
        self.running = False

    def run_once(self):
        return self.controller.run_once()

    def run(
        self,
        number_of_cycles: int = 5,
        interval_seconds: float = 1.0,
    ):
        if number_of_cycles <= 0:
            raise ValueError(
                "number_of_cycles must be greater than 0."
            )

        if interval_seconds < 0:
            raise ValueError(
                "interval_seconds cannot be negative."
            )

        results = []
        self.running = True

        try:
            for cycle in range(number_of_cycles):
                if not self.running:
                    break

                calibration = self.controller.run_once()
                results.append(calibration)

                print(
                    f"Cycle {cycle + 1} | "
                    f"Record ID: {calibration.record_id} | "
                    f"Estimated: {calibration.estimated_value:.4f} | "
                    f"Reference: {calibration.reference_value:.4f} | "
                    f"Status: {calibration.status}"
                )

                if cycle < number_of_cycles - 1:
                    time.sleep(interval_seconds)

        finally:
            self.running = False

        return results

    def stop(self):
        self.running = False