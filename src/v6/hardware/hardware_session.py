from src.v6.hardware.connection_manager import ConnectionManager
from src.v6.hardware.hardware_in_loop import HardwareInLoopController


class HardwareSession:
    """
    Controls the lifecycle of a hardware calibration session.
    """

    def __init__(
        self,
        controller: HardwareInLoopController,
    ):
        self.controller = controller
        self.connection_manager = ConnectionManager(
            controller.pair.instrument
        )

        self.reference = controller.pair.reference

    def start(self):
        self.connection_manager.connect()
        self.reference.connect()

        if not self.controller.safety_manager.check_ready():
            self.stop()
            raise RuntimeError(
                "Hardware session failed safety checks."
            )

    def stop(self):
        self.connection_manager.disconnect()

        if self.reference.is_connected():
            self.reference.disconnect()

    def is_ready(self) -> bool:
        return self.controller.safety_manager.check_ready()

    def run_calibration(self):
        if not self.is_ready():
            raise RuntimeError(
                "Hardware session is not ready."
            )

        return self.controller.run_once()