from src.v6.hardware.reference_standard import ReferenceStandard


class SimulatedReferenceStandard(ReferenceStandard):
    """
    Software-only reference standard simulator.
    """

    def __init__(self, reference_value: float):
        if reference_value <= 0:
            raise ValueError(
                "Reference value must be greater than 0."
            )

        self.reference_value = reference_value
        self._connected = False

    def connect(self):
        self._connected = True

    def disconnect(self):
        self._connected = False

    def is_connected(self) -> bool:
        return self._connected

    def read_reference_value(self) -> float:
        if not self._connected:
            raise RuntimeError(
                "Reference standard is not connected."
            )

        return self.reference_value