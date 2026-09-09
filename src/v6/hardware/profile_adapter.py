import json

from src.v6.hardware.configured_adapter import ConfiguredInstrumentAdapter
from src.v6.hardware.instrument_profile import InstrumentProfile
from src.v6.hardware.profile_validator import validate_profile_measurement


class ProfileDrivenAdapter(ConfiguredInstrumentAdapter):
    """
    Instrument adapter driven by an InstrumentProfile.

    The profile defines identity, command, transport metadata,
    and measurement validation rules.
    """

    def __init__(
        self,
        transport,
        profile: InstrumentProfile,
    ):
        profile.validate()

        super().__init__(
            transport=transport,
            identity={
                "manufacturer": profile.manufacturer,
                "model": profile.model,
                "serial_number": profile.serial_number,
            },
            read_command=profile.read_command,
        )

        self.profile = profile

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

        if not response:
            raise TimeoutError(
                "No measurement response received."
            )

        try:
            measurement = json.loads(
                response.decode("utf-8")
            )
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError(
                "Invalid instrument measurement response."
            ) from exc

        return validate_profile_measurement(
            self.profile,
            measurement,
        )

    def identify(self) -> dict:
        identity = super().identify()

        identity["transport_type"] = (
            self.profile.transport_type
        )

        return identity