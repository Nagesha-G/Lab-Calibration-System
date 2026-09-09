from src.v6.hardware.calibration_pair import CalibrationPair
from src.v6.hardware.hardware_in_loop import HardwareInLoopController
from src.v6.hardware.simulator.simulated_instrument import SimulatedInstrument
from src.v6.hardware.simulator.simulated_reference_standard import (
    SimulatedReferenceStandard,
)
from src.v6.hardware.calibration_orchestrator import CalibrationOrchestrator


def test_orchestrator_runs_multiple_calibrations():
    instrument = SimulatedInstrument(1)
    reference = SimulatedReferenceStandard(2.0)

    pair = CalibrationPair(
        instrument,
        reference,
    )

    pair.connect()

    controller = HardwareInLoopController(
        pair=pair,
        instrument_id=1,
        model_id=1,
    )

    orchestrator = CalibrationOrchestrator(controller)

    results = orchestrator.run(
        number_of_cycles=3,
        interval_seconds=0.1,
    )

    pair.disconnect()

    assert len(results) == 3

    for result in results:
        assert result.record_id is not None
        assert result.reference_value == 2.0
        assert result.status in {"PASS", "FAIL"}


def test_orchestrator_rejects_invalid_cycle_count():
    instrument = SimulatedInstrument(1)
    reference = SimulatedReferenceStandard(2.0)

    pair = CalibrationPair(
        instrument,
        reference,
    )

    pair.connect()

    controller = HardwareInLoopController(
        pair=pair,
        instrument_id=1,
        model_id=1,
    )

    orchestrator = CalibrationOrchestrator(controller)

    try:
        orchestrator.run(number_of_cycles=0)
        assert False, "Invalid cycle count should be rejected."
    except ValueError as exc:
        assert "number_of_cycles" in str(exc)

    pair.disconnect()