from dataclasses import dataclass, field


@dataclass
class MeasurementField:
    name: str
    unit: str
    minimum: float
    maximum: float


@dataclass
class InstrumentProfile:
    manufacturer: str
    model: str
    serial_number: str
    transport_type: str
    read_command: str
    connection: dict = field(default_factory=dict)
    measurement_fields: list[MeasurementField] = field(
        default_factory=list
    )

    def validate(self):
        if not self.manufacturer.strip():
            raise ValueError("manufacturer cannot be empty.")

        if not self.model.strip():
            raise ValueError("model cannot be empty.")

        if not self.serial_number.strip():
            raise ValueError("serial_number cannot be empty.")

        allowed_transports = {
            "simulated",
            "serial",
            "usb",
            "tcp",
        }

        if self.transport_type.lower() not in allowed_transports:
            raise ValueError(
                f"Unsupported transport type: {self.transport_type}"
            )

        if not self.read_command.strip():
            raise ValueError("read_command cannot be empty.")

        if not self.measurement_fields:
            raise ValueError(
                "At least one measurement field is required."
            )

        for field in self.measurement_fields:
            if not field.name.strip():
                raise ValueError(
                    "Measurement field name cannot be empty."
                )

            if field.maximum <= field.minimum:
                raise ValueError(
                    f"Invalid range for field '{field.name}'."
                )

        return True