from src.v6.hardware.instrument_interface import InstrumentInterface


class MeasurementRunner:
    """
    Runs automatic measurement acquisition from an instrument.
    """

    def __init__(self, instrument: InstrumentInterface):
        self.instrument = instrument

    def collect(self) -> dict:
        if not self.instrument.is_connected():
            raise RuntimeError("Instrument is not connected.")

        return self.instrument.read_measurement()