from src.v6.hardware.acquisition_service import AcquisitionService
from src.v6.hardware.fault_injection import FaultInjectingInstrument


def test_acquisition_recovers_after_instrument_failure():
    instrument = FaultInjectingInstrument(
        instrument_id=1,
        fail_count=1,
    )

    instrument.connect()

    service = AcquisitionService(
        instrument=instrument,
        instrument_id=1,
    )

    try:
        service.acquire_once()
        assert False, "First acquisition should have failed."
    except ConnectionError:
        pass

    measurement = service.acquire_once()

    assert measurement.instrument_id == 1
    assert measurement.measurement_id is not None

    instrument.disconnect()