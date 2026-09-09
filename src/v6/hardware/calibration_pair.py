from src.v6.hardware.instrument_interface import InstrumentInterface
from src.v6.hardware.reference_standard import ReferenceStandard


class CalibrationPair:
    """
    Coordinates the instrument under test and the reference standard.
    """

    def __init__(
        self,
        instrument: InstrumentInterface,
        reference: ReferenceStandard,
    ):
        self.instrument = instrument
        self.reference = reference

    def connect(self):
        self.instrument.connect()
        self.reference.connect()

    def disconnect(self):
        self.instrument.disconnect()
        self.reference.disconnect()

    def is_ready(self) -> bool:
        return (
            self.instrument.is_connected()
            and self.reference.is_connected()
        )

    def read_calibration_data(self):
        if not self.is_ready():
            raise RuntimeError(
                "Instrument and reference standard must be connected."
            )

        measurement = self.instrument.read_measurement()
        reference_value = self.reference.read_reference_value()

        return {
            "measurement": measurement,
            "reference_value": reference_value,
        }