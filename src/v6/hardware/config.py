import hashlib
import json
from pathlib import Path

import pytest

from src.v5.database.database import Base, SessionLocal, engine
from src.v5.database.models import (
    CalibrationPolicy,
    Instrument,
    InstrumentConfiguration,
    Model,
)


MODEL_ID = 5
MODEL_PATH = Path("models/v2/co_calibration_model.joblib")


def calculate_hash(path: Path) -> str:
    sha256 = hashlib.sha256()

    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(8192), b""):
            sha256.update(chunk)

    return sha256.hexdigest()


@pytest.fixture(autouse=True)
def ensure_v6_dependencies():
    """
    Ensure every V6 test has the instrument, configuration,
    calibration policy, and approved V2 model it requires.
    """

    Base.metadata.create_all(bind=engine)

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Required calibration model not found: {MODEL_PATH}"
        )

    db = SessionLocal()

    try:
        # -------------------------------------------------
        # Instrument
        # -------------------------------------------------
        instrument = (
            db.query(Instrument)
            .filter(Instrument.instrument_id == 1)
            .first()
        )

        if instrument is None:
            instrument = Instrument(
                instrument_id=1,
                name="V6 Test Gas Analyzer",
                manufacturer="Lab Calibration System",
                model="V6-TEST",
                serial_number="V6-TEST-001",
                instrument_type="gas_analyzer",
                status="active",
            )

            db.add(instrument)
            db.commit()
            db.refresh(instrument)

        # -------------------------------------------------
        # Instrument configuration
        # -------------------------------------------------
        configuration = (
            db.query(InstrumentConfiguration)
            .filter(
                InstrumentConfiguration.instrument_id == 1,
                InstrumentConfiguration.active.is_(True),
            )
            .first()
        )

        if configuration is None:
            configuration = InstrumentConfiguration(
                instrument_id=1,
                configuration_name="V6 Test Configuration",
                input_schema=json.dumps(
                    {
                        "PT08.S1(CO)": "PT08.S1(CO)",
                        "PT08.S2(NMHC)": "PT08.S2(NMHC)",
                        "PT08.S3(NOx)": "PT08.S3(NOx)",
                        "PT08.S4(NO2)": "PT08.S4(NO2)",
                        "PT08.S5(O3)": "PT08.S5(O3)",
                        "T": "T",
                        "RH": "RH",
                        "AH": "AH",
                    }
                ),
                target_variable="CO(GT)",
                unit="mg/m3",
                active=True,
            )

            db.add(configuration)
            db.commit()

        # -------------------------------------------------
        # Calibration policy
        # -------------------------------------------------
        policy = (
            db.query(CalibrationPolicy)
            .filter(
                CalibrationPolicy.instrument_id == 1,
                CalibrationPolicy.active.is_(True),
            )
            .first()
        )

        if policy is None:
            policy = CalibrationPolicy(
                instrument_id=1,
                calibration_interval_days=30,
                tolerance=0.5,
                reference_required=True,
                active=True,
            )

            db.add(policy)
            db.commit()

        # -------------------------------------------------
        # V2 calibration model
        # -------------------------------------------------
        model = (
            db.query(Model)
            .filter(Model.model_id == MODEL_ID)
            .first()
        )

        if model is None:
            model = Model(
                model_id=MODEL_ID,
                model_name="V6 Test CO Calibration Model",
                model_version="v2.0.0",
                instrument_type="gas_analyzer",
                target_variable="CO(GT)",
                framework="scikit-learn",
                artifact_path=str(MODEL_PATH),
                artifact_hash=calculate_hash(MODEL_PATH),
                status="approved",
            )

            db.add(model)
            db.commit()

    finally:
        db.close()