from src.v6.hardware.acquisition_service import AcquisitionService
from src.v6.hardware.simulator.simulated_instrument import SimulatedInstrument


def test_acquisition_service_stores_measurement():
    instrument = SimulatedInstrument(1)
    instrument.connect()

    service = AcquisitionService(
        instrument=instrument,
        instrument_id=1,
    )

    measurement = service.acquire_once()

    instrument.disconnect()

    assert measurement.instrument_id == 1
    assert measurement.measurement_id is not None