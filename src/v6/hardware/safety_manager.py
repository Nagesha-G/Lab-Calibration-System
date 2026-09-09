from src.v6.hardware.instrument_interface import InstrumentInterface
from src.v6.hardware.reference_standard import ReferenceStandard


class SafetyManager:
    """
    Performs basic safety checks before a calibration cycle.
    """

    def __init__(
        self,
        instrument: InstrumentInterface,
        reference: ReferenceStandard,
    ):
        self.instrument = instrument
        self.reference = reference

    def check_ready(self) -> bool:
        if not self.instrument.is_connected():
            return False

        if not self.reference.is_connected():
            return False

        return True

    def require_ready(self):
        if not self.instrument.is_connected():
            raise RuntimeError(
                "Instrument is not connected."
            )

        if not self.reference.is_connected():
            raise RuntimeError(
                "Reference standard is not connected."
            )