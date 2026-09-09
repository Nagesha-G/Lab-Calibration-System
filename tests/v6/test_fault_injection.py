from src.v6.hardware.fault_injection import FaultInjectingInstrument


def test_fault_occurs_then_recovers():
    instrument = FaultInjectingInstrument(
        instrument_id=1,
        fail_count=1,
    )

    instrument.connect()

    try:
        instrument.read_measurement()
        assert False, "First read should have failed."
    except ConnectionError as exc:
        assert "communication failure" in str(exc)

    measurement = instrument.read_measurement()

    assert isinstance(measurement, dict)
    assert "PT08.S1(CO)" in measurement
    assert "RH" in measurement

    instrument.disconnect()