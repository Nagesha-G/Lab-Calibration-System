import pytest

from src.v5.database.database import SessionLocal
from src.v5.database.models import (
    Instrument,
    InstrumentConfiguration,
    CalibrationPolicy,
)


@pytest.fixture(autouse=True)
def ensure_v6_test_data():
    db = SessionLocal()

    try:
        # ---------------------------------------------------------
        # Instrument
        # ---------------------------------------------------------
        instrument = (
            db.query(Instrument)
            .filter(Instrument.instrument_id == 1)
            .first()
        )

        if instrument is None:
            instrument = Instrument(
                instrument_id=1,
                name="V6 Test Instrument",
                manufacturer="Lab Calibration System",
                model="Simulated Gas Analyzer",
                serial_number="V6-TEST-001",
                instrument_type="gas_analyzer",
                status="active",
            )

            db.add(instrument)
            db.commit()
            db.refresh(instrument)

        # ---------------------------------------------------------
        # Active instrument configuration
        # ---------------------------------------------------------
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
                configuration_name="V6 Test Gas Analyzer Configuration",

                # V5 calibration engine expects:
                # model column -> measurement key
                input_schema=(
                    '{'
                    '"PT08.S1(CO)": "PT08.S1(CO)", '
                    '"PT08.S2(NMHC)": "PT08.S2(NMHC)", '
                    '"PT08.S3(NOx)": "PT08.S3(NOx)", '
                    '"PT08.S4(NO2)": "PT08.S4(NO2)", '
                    '"PT08.S5(O3)": "PT08.S5(O3)", '
                    '"T": "T", '
                    '"RH": "RH", '
                    '"AH": "AH"'
                    '}'
                ),

                target_variable="CO(GT)",
                unit="mg/m3",
                active=True,
            )

            db.add(configuration)
            db.commit()

        # ---------------------------------------------------------
        # Active calibration policy
        # ---------------------------------------------------------
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
                tolerance=1.0,
                reference_required=True,
                active=True,
            )

            db.add(policy)
            db.commit()

    finally:
        db.close()