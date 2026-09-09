from src.v6.hardware.hardware_in_loop import HardwareInLoopController


class SafeCalibrationRunner:
    """
    Executes calibration only when the hardware safety checks pass.
    """

    def __init__(self, controller: HardwareInLoopController):
        self.controller = controller

    def run_once(self):
        if not self.controller.safety_manager.check_ready():
            raise RuntimeError(
                "Calibration blocked: hardware is not ready."
            )

        return self.controller.run_once()