from src.v6.hardware.instrument_interface import InstrumentInterface
from src.v6.hardware.serial_protocol import decode_measurement


class SerialInstrument(InstrumentInterface):
    """
    Serial/COM instrument driver.

    Supports command-based request/response communication.
    """

    def __init__(
        self,
        port: str,
        baudrate: int = 9600,
        timeout: float = 2.0,
        newline: bytes = b"\n",
    ):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.newline = newline
        self._serial = None

    def connect(self):
        import serial

        if self._serial is not None and self._serial.is_open:
            return

        self._serial = serial.Serial(
            port=self.port,
            baudrate=self.baudrate,
            timeout=self.timeout,
            write_timeout=self.timeout,
        )

    def disconnect(self):
        if self._serial is not None and self._serial.is_open:
            self._serial.close()

        self._serial = None

    def is_connected(self) -> bool:
        return (
            self._serial is not None
            and self._serial.is_open
        )

    def send_command(self, command: str) -> bytes:
        if not self.is_connected():
            raise RuntimeError(
                "Serial instrument is not connected."
            )

        if not command or not command.strip():
            raise ValueError(
                "Command cannot be empty."
            )

        message = (
            command.strip().encode("utf-8")
            + self.newline
        )

        self._serial.write(message)
        self._serial.flush()

        response = self._serial.readline()

        if not response:
            raise TimeoutError(
                "No response received before serial timeout."
            )

        return response

    def read_measurement(self) -> dict:
        response = self.send_command("READ?")

        return decode_measurement(response)