from src.v6.hardware.instrument_interface import InstrumentInterface
from src.v6.hardware.v5_bridge import acquire_and_store_measurement


class AcquisitionService:
    """
    Continuously acquires measurements from an instrument
    and stores them in the V5 measurement system.
    """

    def __init__(
        self,
        instrument: InstrumentInterface,
        instrument_id: int,
    ):
        self.instrument = instrument
        self.instrument_id = instrument_id

    def acquire_once(self):
        if not self.instrument.is_connected():
            raise RuntimeError("Instrument is not connected.")

        return acquire_and_store_measurement(
            instrument=self.instrument,
            instrument_id=self.instrument_id,
        )