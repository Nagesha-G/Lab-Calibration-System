from abc import ABC, abstractmethod


class InstrumentInterface(ABC):
    """
    Common interface for all instruments.

    Every real or simulated instrument must implement
    these operations.
    """

    @abstractmethod
    def connect(self):
        """Connect to the instrument."""
        raise NotImplementedError

    @abstractmethod
    def disconnect(self):
        """Disconnect from the instrument."""
        raise NotImplementedError

    @abstractmethod
    def is_connected(self) -> bool:
        """Return whether the instrument is connected."""
        raise NotImplementedError

    @abstractmethod
    def read_measurement(self) -> dict:
        """Read one measurement from the instrument."""
        raise NotImplementedError