from src.v6.hardware.instrument_config import InstrumentConfig
from src.v6.hardware.driver_registry import create_instrument_driver
from src.v6.hardware.instrument_adapter import InstrumentAdapter
from src.v6.hardware.configured_adapter import ConfiguredInstrumentAdapter


def create_configured_driver(
    config: InstrumentConfig,
):
    config.validate()

    transport_type = config.transport_type.lower()

    transport = create_instrument_driver(
        transport_type,
        **config.connection,
        **(
            {"instrument_id": 1}
            if transport_type == "simulated"
            else {}
        ),
    )

    identity = {
        "manufacturer": config.manufacturer,
        "model": config.model,
        "serial_number": config.serial_number,
    }

    adapter = ConfiguredInstrumentAdapter(
        transport=transport,
        identity=identity,
        read_command=config.read_command,
    )

    if not isinstance(adapter, InstrumentAdapter):
        raise TypeError(
            "Configured driver must implement InstrumentAdapter."
        )

    return adapter