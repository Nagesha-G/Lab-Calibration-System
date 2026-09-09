import time

from src.v6.hardware.instrument_interface import InstrumentInterface


def stream_measurements(
    instrument: InstrumentInterface,
    interval_seconds: float = 1.0,
    number_of_measurements: int = 10,
):
    """
    Read measurements continuously from an instrument.
    """

    if interval_seconds <= 0:
        raise ValueError("Interval must be greater than 0.")

    if number_of_measurements <= 0:
        raise ValueError("Number of measurements must be greater than 0.")

    if not instrument.is_connected():
        raise RuntimeError("Instrument is not connected.")

    for _ in range(number_of_measurements):
        measurement = instrument.read_measurement()

        yield measurement

        time.sleep(interval_seconds)