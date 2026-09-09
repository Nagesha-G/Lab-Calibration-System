from abc import ABC, abstractmethod

from src.v6.hardware.instrument_interface import InstrumentInterface


class InstrumentAdapter(ABC):
    """
    Manufacturer-specific instrument adapter.

    The adapter translates an instrument's proprietary
    commands and responses into the common InstrumentInterface.
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
    def read_measurement(self) -> dict:
        raise NotImplementedError

    @abstractmethod
    def identify(self) -> dict:
        """
        Return instrument identity information.
        """
        raise NotImplementedError