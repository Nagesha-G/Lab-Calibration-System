from src.v6.hardware.instrument_interface import InstrumentInterface


class ConnectionManager:
    """
    Manages instrument connection and basic recovery.
    """

    def __init__(self, instrument: InstrumentInterface):
        self.instrument = instrument

    def connect(self):
        if self.instrument.is_connected():
            return

        self.instrument.connect()

    def disconnect(self):
        if not self.instrument.is_connected():
            return

        self.instrument.disconnect()

    def reconnect(self):
        self.disconnect()
        self.connect()

    def is_connected(self) -> bool:
        return self.instrument.is_connected()

    def ensure_connected(self, max_attempts: int = 3) -> bool:
        if max_attempts < 1:
            raise ValueError("max_attempts must be greater than 0.")

        if self.is_connected():
            return True

        for _ in range(max_attempts):
            try:
                self.connect()

                if self.is_connected():
                    return True

            except Exception:
                continue

        return False