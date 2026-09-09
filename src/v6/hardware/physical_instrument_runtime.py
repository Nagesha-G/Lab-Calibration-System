"""
Physical Instrument Runtime
===========================

Runtime for connecting the Lab Calibration System to a real
serial/COM instrument.

The transport layer is separated from the instrument profile so
manufacturer-specific command and measurement definitions can be
configured without changing the calibration engine.
"""

from dataclasses import dataclass, field

from src.v6.hardware.instrument_profile import (
    InstrumentProfile,
    MeasurementField,
)
from src.v6.hardware.profile_adapter import ProfileDrivenAdapter
from src.v6.hardware.serial_instrument import SerialInstrument


@dataclass
class PhysicalInstrumentConfig:
    """
    Configuration required to connect to a real instrument.
    """

    manufacturer: str
    model: str
    serial_number: str

    port: str

    baudrate: int = 9600
    timeout: float = 2.0

    read_command: str = "READ?"

    measurement_fields: list[MeasurementField] = field(
        default_factory=list
    )

    def validate(self):
        if not self.manufacturer.strip():
            raise ValueError(
                "manufacturer cannot be empty."
            )

        if not self.model.strip():
            raise ValueError(
                "model cannot be empty."
            )

        if not self.serial_number.strip():
            raise ValueError(
                "serial_number cannot be empty."
            )

        if not self.port.strip():
            raise ValueError(
                "port cannot be empty."
            )

        if self.baudrate <= 0:
            raise ValueError(
                "baudrate must be greater than 0."
            )

        if self.timeout <= 0:
            raise ValueError(
                "timeout must be greater than 0."
            )

        if not self.read_command.strip():
            raise ValueError(
                "read_command cannot be empty."
            )

        if not self.measurement_fields:
            raise ValueError(
                "measurement_fields cannot be empty."
            )

        for field in self.measurement_fields:
            if field.maximum <= field.minimum:
                raise ValueError(
                    f"Invalid range for field '{field.name}'."
                )

        return True


class PhysicalInstrumentRuntime:
    """
    High-level runtime for a real serial instrument.

    Responsibilities:
    - validate physical instrument configuration
    - build the serial transport
    - build the profile-driven adapter
    - connect/disconnect
    - report connection state
    - acquire validated measurements
    """

    def __init__(
        self,
        config: PhysicalInstrumentConfig,
    ):
        config.validate()

        self.config = config

        self.profile = InstrumentProfile(
            manufacturer=config.manufacturer,
            model=config.model,
            serial_number=config.serial_number,
            transport_type="serial",
            read_command=config.read_command,
            connection={
                "port": config.port,
                "baudrate": config.baudrate,
                "timeout": config.timeout,
            },
            measurement_fields=config.measurement_fields,
        )

        self.transport = SerialInstrument(
            port=config.port,
            baudrate=config.baudrate,
            timeout=config.timeout,
        )

        self.adapter = ProfileDrivenAdapter(
            transport=self.transport,
            profile=self.profile,
        )

    def connect(self):
        """
        Open the real serial/COM connection.
        """
        self.adapter.connect()

        if not self.adapter.is_connected():
            raise ConnectionError(
                f"Unable to connect to {self.config.port}."
            )

    def disconnect(self):
        """
        Close the real serial/COM connection.
        """
        self.adapter.disconnect()

    def is_connected(self) -> bool:
        """
        Return current connection state.
        """
        return self.adapter.is_connected()

    def identify(self) -> dict:
        """
        Return configured instrument identity.
        """
        return self.adapter.identify()

    def read_measurement(self) -> dict:
        """
        Acquire one validated measurement from the real instrument.
        """
        if not self.is_connected():
            raise RuntimeError(
                "Physical instrument is not connected."
            )

        return self.adapter.read_measurement()


def create_gas_analyzer_runtime(
    port: str,
    manufacturer: str,
    model: str,
    serial_number: str,
    baudrate: int = 9600,
    timeout: float = 2.0,
    read_command: str = "READ?",
) -> PhysicalInstrumentRuntime:
    """
    Convenience factory for the current gas-analyzer measurement model.
    """

    measurement_fields = [
        MeasurementField(
            name="PT08.S1(CO)",
            unit="sensor_units",
            minimum=0,
            maximum=5000,
        ),
        MeasurementField(
            name="PT08.S2(NMHC)",
            unit="sensor_units",
            minimum=0,
            maximum=5000,
        ),
        MeasurementField(
            name="PT08.S3(NOx)",
            unit="sensor_units",
            minimum=0,
            maximum=5000,
        ),
        MeasurementField(
            name="PT08.S4(NO2)",
            unit="sensor_units",
            minimum=0,
            maximum=5000,
        ),
        MeasurementField(
            name="PT08.S5(O3)",
            unit="sensor_units",
            minimum=0,
            maximum=5000,
        ),
        MeasurementField(
            name="T",
            unit="degC",
            minimum=-40,
            maximum=85,
        ),
        MeasurementField(
            name="RH",
            unit="%",
            minimum=0,
            maximum=100,
        ),
        MeasurementField(
            name="AH",
            unit="absolute_humidity",
            minimum=0,
            maximum=10,
        ),
    ]

    config = PhysicalInstrumentConfig(
        manufacturer=manufacturer,
        model=model,
        serial_number=serial_number,
        port=port,
        baudrate=baudrate,
        timeout=timeout,
        read_command=read_command,
        measurement_fields=measurement_fields,
    )

    return PhysicalInstrumentRuntime(config)