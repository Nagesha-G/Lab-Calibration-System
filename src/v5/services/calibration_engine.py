from datetime import datetime

import pandas as pd

from src.v5.database.database import SessionLocal
from src.v5.database.models import (
    Instrument,
    InstrumentConfiguration,
    CalibrationPolicy,
    Model,
    Measurement,
    CalibrationRecord,
)
from src.v5.services.measurement_service import (
    parse_measurement_data,
)


def run_calibration(
    instrument_id: int,
    measurement_id: int,
    model_id: int,
    reference_value: float,
):
    db = SessionLocal()

    try:
        # -------------------------------------------------
        # 1. Validate instrument
        # -------------------------------------------------
        instrument = (
            db.query(Instrument)
            .filter(
                Instrument.instrument_id == instrument_id
            )
            .first()
        )

        if instrument is None:
            raise ValueError(
                f"Instrument {instrument_id} does not exist."
            )

        # -------------------------------------------------
        # 2. Validate measurement
        # -------------------------------------------------
        measurement = (
            db.query(Measurement)
            .filter(
                Measurement.measurement_id
                == measurement_id,
                Measurement.instrument_id
                == instrument_id,
            )
            .first()
        )

        if measurement is None:
            raise ValueError(
                "Measurement does not exist for this instrument."
            )

        # -------------------------------------------------
        # 3. Validate model
        # -------------------------------------------------
        model = (
            db.query(Model)
            .filter(
                Model.model_id == model_id
            )
            .first()
        )

        if model is None:
            raise ValueError(
                f"Model {model_id} does not exist."
            )

        if model.status != "approved":
            raise ValueError(
                "Model must be approved before calibration."
            )

        # -------------------------------------------------
        # 4. Validate configuration
        # -------------------------------------------------
        configuration = (
            db.query(InstrumentConfiguration)
            .filter(
                InstrumentConfiguration.instrument_id
                == instrument_id,
                InstrumentConfiguration.active == True,
            )
            .first()
        )

        if configuration is None:
            raise ValueError(
                "No active instrument configuration exists."
            )

        # -------------------------------------------------
        # 5. Validate policy
        # -------------------------------------------------
        policy = (
            db.query(CalibrationPolicy)
            .filter(
                CalibrationPolicy.instrument_id
                == instrument_id,
                CalibrationPolicy.active == True,
            )
            .first()
        )

        if policy is None:
            raise ValueError(
                "No active calibration policy exists."
            )

        # -------------------------------------------------
        # 6. Validate reference value
        # -------------------------------------------------
        if reference_value <= 0:
            raise ValueError(
                "Reference value must be greater than 0."
            )

        # -------------------------------------------------
        # 7. Load measurement data
        # -------------------------------------------------
        measurement_data = parse_measurement_data(
            measurement
        )

        # -------------------------------------------------
        # 8. Parse configuration schema
        # -------------------------------------------------
        import json

        input_schema = json.loads(
            configuration.input_schema
        )

        if not input_schema:
            raise ValueError(
                "Instrument configuration has no inputs."
            )

        # -------------------------------------------------
        # 9. Build model input
        # -------------------------------------------------
        model_input = {}

        for model_column, measurement_key in input_schema.items():

            if measurement_key not in measurement_data:
                raise ValueError(
                    f"Measurement is missing required input: "
                    f"{measurement_key}"
                )

            model_input[model_column] = measurement_data[
                measurement_key
            ]

        input_dataframe = pd.DataFrame(
            [model_input]
        )

        # -------------------------------------------------
        # 10. Load model artifact
        # -------------------------------------------------
        import joblib

        estimator = joblib.load(
            model.artifact_path
        )

        # -------------------------------------------------
        # 11. Verify target variable
        # -------------------------------------------------
        if configuration.target_variable != model.target_variable:
            raise ValueError(
                "Configuration target does not match model target."
            )

        # -------------------------------------------------
        # 12. Generate prediction
        # -------------------------------------------------
        raw_prediction = float(
            estimator.predict(input_dataframe)[0]
        )

        # Physical non-negative constraint.
        estimated_value = max(
            0.0,
            raw_prediction
        )

        # -------------------------------------------------
        # 13. Calculate calibration result
        # -------------------------------------------------
        error = round(
            estimated_value - reference_value,
                10
            )

        absolute_error = round(
        abs(error),
        10
            )

        absolute_error = abs(error)

        if absolute_error <= policy.tolerance:
            status = "PASS"
        else:
            status = "FAIL"

        # -------------------------------------------------
        # 14. Create calibration record
        # -------------------------------------------------
        record = CalibrationRecord(
            instrument_id=instrument_id,
            model_id=model_id,
            measurement_id=measurement_id,
            measurement_time=measurement.created_at,
            estimated_value=estimated_value,
            reference_value=reference_value,
            error=error,
            absolute_error=absolute_error,
            tolerance=policy.tolerance,
            status=status,
            created_at=datetime.now(),
        )

        db.add(record)
        db.commit()
        db.refresh(record)

        return record

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()