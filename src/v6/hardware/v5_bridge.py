from src.v5.services.measurement_service import create_measurement
from src.v6.hardware.instrument_interface import InstrumentInterface


def acquire_and_store_measurement(
    instrument: InstrumentInterface,
    instrument_id: int,
):
    if not instrument.is_connected():
        raise RuntimeError("Instrument is not connected.")

    measurement_data = instrument.read_measurement()

    measurement = create_measurement(
        instrument_id=instrument_id,
        measurement_data=measurement_data,
    )

    return measurement