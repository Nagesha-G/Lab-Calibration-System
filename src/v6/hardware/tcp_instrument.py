import socket

from src.v6.hardware.instrument_interface import InstrumentInterface
from src.v6.hardware.serial_protocol import decode_measurement


class TCPInstrument(InstrumentInterface):
    """
    TCP/IP instrument driver abstraction.

    Communicates with a network-connected instrument using
    a request/response protocol.
    """

    def __init__(
        self,
        host: str,
        port: int,
        timeout: float = 2.0,
    ):
        if not host or not host.strip():
            raise ValueError("host cannot be empty.")

        if port < 1 or port > 65535:
            raise ValueError("port must be between 1 and 65535.")

        if timeout <= 0:
            raise ValueError("timeout must be greater than 0.")

        self.host = host
        self.port = port
        self.timeout = timeout
        self._socket = None

    def connect(self):
        if self.is_connected():
            return

        self._socket = socket.create_connection(
            (self.host, self.port),
            timeout=self.timeout,
        )

    def disconnect(self):
        if self._socket is not None:
            self._socket.close()

        self._socket = None

    def is_connected(self) -> bool:
        return self._socket is not None

    def send_command(self, command: str) -> bytes:
        if not self.is_connected():
            raise RuntimeError(
                "TCP instrument is not connected."
            )

        if not command or not command.strip():
            raise ValueError(
                "Command cannot be empty."
            )

        message = (
            command.strip().encode("utf-8")
            + b"\n"
        )

        try:
            self._socket.sendall(message)
            response = self._socket.recv(4096)
        except socket.timeout as exc:
            raise TimeoutError(
                "No TCP response received before timeout."
            ) from exc

        if not response:
            raise ConnectionError(
                "TCP instrument closed the connection."
            )

        return response

    def read_measurement(self) -> dict:
        response = self.send_command("READ?")
        return decode_measurement(response)