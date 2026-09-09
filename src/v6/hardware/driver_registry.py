from src.v6.hardware.instrument_interface import InstrumentInterface
from src.v6.hardware.simulator.simulated_instrument import SimulatedInstrument
from src.v6.hardware.serial_instrument import SerialInstrument
from src.v6.hardware.usb_instrument import USBInstrument
from src.v6.hardware.tcp_instrument import TCPInstrument


def create_instrument_driver(
    driver_type: str,
    **kwargs,
) -> InstrumentInterface:
    """
    Create an instrument driver from a driver type.
    """

    if not driver_type or not driver_type.strip():
        raise ValueError("driver_type cannot be empty.")

    drivers = {
        "simulated": SimulatedInstrument,
        "serial": SerialInstrument,
        "usb": USBInstrument,
        "tcp": TCPInstrument,
    }

    driver_class = drivers.get(driver_type.lower())

    if driver_class is None:
        raise ValueError(
            f"Unsupported driver type: {driver_type}"
        )

    instrument = driver_class(**kwargs)

    if not isinstance(instrument, InstrumentInterface):
        raise TypeError(
            "Instrument driver must implement InstrumentInterface."
        )

    return instrument