from abc import ABC, abstractmethod


class ReferenceStandard(ABC):
    """
    Common interface for a calibration reference standard.
    """

    @abstractmethod
    def connect(self):
        raise NotImplementedError

    @abstractmethod
    def disconnect(self):
        raise NotImplementedError

    @abstractmethod
    def is_connected(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def read_reference_value(self) -> float:
        raise NotImplementedError