from src.v5.services.calibration_engine import run_calibration
from src.v6.hardware.calibration_pair import CalibrationPair
from src.v6.hardware.reference_validator import validate_reference_value
from src.v6.hardware.v5_bridge import acquire_and_store_measurement
from src.v6.hardware.safety_manager import SafetyManager


class HardwareInLoopController:
    """
    Coordinates an instrument and reference standard
    for a protected calibration cycle.
    """

    def __init__(
        self,
        pair: CalibrationPair,
        instrument_id: int,
        model_id: int,
    ):
        self.pair = pair
        self.instrument_id = instrument_id
        self.model_id = model_id

        self.safety_manager = SafetyManager(
            instrument=self.pair.instrument,
            reference=self.pair.reference,
        )

    def run_once(self):
        self.safety_manager.require_ready()

        reference_value = validate_reference_value(
            self.pair.reference
        )

        measurement = acquire_and_store_measurement(
            instrument=self.pair.instrument,
            instrument_id=self.instrument_id,
        )

        calibration = run_calibration(
            instrument_id=self.instrument_id,
            measurement_id=measurement.measurement_id,
            model_id=self.model_id,
            reference_value=reference_value,
        )

        return calibration