import random

from src.v6.hardware.instrument_interface import InstrumentInterface


class SimulatedInstrument(InstrumentInterface):
    """
    Software-only instrument simulator.

    Generates measurements using the same sensor names
    expected by the V2 calibration model.
    """

    def __init__(self, instrument_id: int):
        self.instrument_id = instrument_id
        self._connected = False

    def connect(self):
        self._connected = True

    def disconnect(self):
        self._connected = False

    def is_connected(self) -> bool:
        return self._connected

    def read_measurement(self) -> dict:
        if not self._connected:
            raise RuntimeError("Instrument is not connected.")

        return {
            "PT08.S1(CO)": random.uniform(800, 1800),
            "PT08.S2(NMHC)": random.uniform(500, 2000),
            "PT08.S3(NOx)": random.uniform(300, 2000),
            "PT08.S4(NO2)": random.uniform(500, 2500),
            "PT08.S5(O3)": random.uniform(500, 2500),
            "T": random.uniform(5, 35),
            "RH": random.uniform(20, 90),
            "AH": random.uniform(0.2, 2.5),
        }