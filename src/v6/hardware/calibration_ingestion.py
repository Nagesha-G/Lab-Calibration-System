from src.v6.hardware.calibration_bridge import acquire_and_calibrate
from src.v6.hardware.instrument_interface import InstrumentInterface


class CalibrationIngestionService:
    """
    Acquires a measurement from an instrument and immediately
    sends it through the V5 calibration engine.
    """

    def __init__(
        self,
        instrument: InstrumentInterface,
        instrument_id: int,
        model_id: int,
        reference_value: float,
    ):
        self.instrument = instrument
        self.instrument_id = instrument_id
        self.model_id = model_id
        self.reference_value = reference_value

    def calibrate_once(self):
        if not self.instrument.is_connected():
            raise RuntimeError("Instrument is not connected.")

        return acquire_and_calibrate(
            instrument=self.instrument,
            instrument_id=self.instrument_id,
            model_id=self.model_id,
            reference_value=self.reference_value,
        )