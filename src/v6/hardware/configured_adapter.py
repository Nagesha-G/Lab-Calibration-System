from src.v6.hardware.instrument_adapter import InstrumentAdapter
from src.v6.hardware.instrument_interface import InstrumentInterface


class ConfiguredInstrumentAdapter(InstrumentAdapter):
    """
    Adapter that translates configured commands and responses
    for an underlying transport.
    """

    def __init__(
        self,
        transport: InstrumentInterface,
        identity: dict,
        read_command: str = "READ?",
    ):
        if not isinstance(transport, InstrumentInterface):
            raise TypeError(
                "transport must implement InstrumentInterface."
            )

        if not isinstance(identity, dict) or not identity:
            raise ValueError(
                "identity must be a non-empty dictionary."
            )

        if not read_command or not read_command.strip():
            raise ValueError(
                "read_command cannot be empty."
            )

        self.transport = transport
        self.identity = identity
        self.read_command = read_command

    def connect(self):
        self.transport.connect()

    def disconnect(self):
        self.transport.disconnect()

    def is_connected(self) -> bool:
        return self.transport.is_connected()

    def read_measurement(self) -> dict:
        if not self.is_connected():
            raise RuntimeError(
                "Instrument adapter is not connected."
            )

        send_command = getattr(
            self.transport,
            "send_command",
            None,
        )

        if send_command is None:
            raise RuntimeError(
                "Underlying transport does not support commands."
            )

        response = send_command(self.read_command)

        from src.v6.hardware.serial_protocol import (
            decode_measurement,
        )

        return decode_measurement(response)

    def identify(self) -> dict:
        return self.identity.copy()