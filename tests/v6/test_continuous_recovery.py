from src.v6.hardware.acquisition_service import AcquisitionService
from src.v6.hardware.continuous_acquisition import run_acquisition
from src.v6.hardware.fault_injection import FaultInjectingInstrument


def test_continuous_acquisition_survives_temporary_failure():
    instrument = FaultInjectingInstrument(
        instrument_id=1,
        fail_count=1,
    )

    instrument.connect()

    service = AcquisitionService(
        instrument=instrument,
        instrument_id=1,
    )

    result = run_acquisition(
        service=service,
        interval_seconds=0.1,
        number_of_cycles=3,
    )

    instrument.disconnect()

    assert len(result["measurements"]) == 2
    assert len(result["errors"]) == 1
    assert result["errors"][0]["cycle"] == 1