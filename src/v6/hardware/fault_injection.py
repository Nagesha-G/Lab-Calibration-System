from src.v6.hardware.simulator.simulated_instrument import (
    SimulatedInstrument,
)


class FaultInjectingInstrument(SimulatedInstrument):
    """
    Simulated instrument that can deliberately fail reads.
    """

    def __init__(self, instrument_id: int, fail_count: int = 1):
        super().__init__(instrument_id)

        if fail_count < 0:
            raise ValueError("fail_count cannot be negative.")

        self.fail_count = fail_count

    def read_measurement(self) -> dict:
        if not self.is_connected():
            raise RuntimeError("Instrument is not connected.")

        if self.fail_count > 0:
            self.fail_count -= 1
            raise ConnectionError(
                "Simulated instrument communication failure."
            )

        return super().read_measurement()