from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import pandas as pd
from sqlalchemy import text

from src.v3.database import SessionLocal
from src.v3.models import Instrument, CalibrationRecord
from src.v3.calibration_service import save_calibration
from src.v4.scheduler.calibration_scheduler import get_due_instruments


# ============================================================
# CONFIGURATION
# ============================================================

MODEL_FILE = "models/v2/co_calibration_model.joblib"
MODEL_VERSION = "v2.0.0"


# ============================================================
# LOAD MACHINE LEARNING MODEL
# ============================================================

model = joblib.load(MODEL_FILE)


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="Lab Calibration System API",
    description="API for the Lab Calibration System",
    version="4.0.0"
)


# ============================================================
# REQUEST MODELS
# ============================================================

class InstrumentCreate(BaseModel):
    name: str
    manufacturer: str
    model: str
    serial_number: str
    instrument_type: str


class CalibrationCreate(BaseModel):
    instrument_id: int

    sensor_1: float
    sensor_2: float
    sensor_3: float
    sensor_4: float
    sensor_5: float

    temperature: float
    humidity: float
    absolute_humidity: float

    reference_value: float
    tolerance: float


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():
    return {
        "message": "Lab Calibration System API",
        "version": "4.0.0",
        "status": "running",
        "endpoints": 21
    }


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


# ============================================================
# INSTRUMENTS
# ============================================================

@app.get("/instruments")
def get_instruments():

    db = SessionLocal()

    try:

        instruments = db.query(Instrument).all()

        return [
            {
                "instrument_id": instrument.instrument_id,
                "name": instrument.name,
                "manufacturer": instrument.manufacturer,
                "model": instrument.model,
                "serial_number": instrument.serial_number,
                "instrument_type": instrument.instrument_type,
                "status": instrument.status
            }
            for instrument in instruments
        ]

    finally:

        db.close()


# ============================================================
# INSTRUMENT OVERVIEW
# ============================================================

@app.get("/instruments/overview")
def get_instruments_overview():

    db = SessionLocal()

    try:

        instruments = db.query(Instrument).all()

        results = []

        for instrument in instruments:

            calibration_count = (
                db.query(CalibrationRecord)
                .filter(
                    CalibrationRecord.instrument_id
                    == instrument.instrument_id
                )
                .count()
            )

            results.append(
                {
                    "instrument_id": instrument.instrument_id,
                    "name": instrument.name,
                    "manufacturer": instrument.manufacturer,
                    "model": instrument.model,
                    "serial_number": instrument.serial_number,
                    "instrument_type": instrument.instrument_type,
                    "status": instrument.status,
                    "calibration_count": calibration_count
                }
            )

        return results

    finally:

        db.close()


# ============================================================
# GET SINGLE INSTRUMENT
# ============================================================

@app.get("/instruments/{instrument_id}")
def get_instrument(instrument_id: int):

    db = SessionLocal()

    try:

        instrument = (
            db.query(Instrument)
            .filter(
                Instrument.instrument_id == instrument_id
            )
            .first()
        )

        if instrument is None:
            return {
                "error": "Instrument not found"
            }

        return {
            "instrument_id": instrument.instrument_id,
            "name": instrument.name,
            "manufacturer": instrument.manufacturer,
            "model": instrument.model,
            "serial_number": instrument.serial_number,
            "instrument_type": instrument.instrument_type,
            "status": instrument.status
        }

    finally:

        db.close()


# ============================================================
# CREATE INSTRUMENT
# ============================================================

@app.post("/instruments")
def create_instrument(instrument_data: InstrumentCreate):

    db = SessionLocal()

    try:

        existing_instrument = (
            db.query(Instrument)
            .filter(
                Instrument.serial_number
                == instrument_data.serial_number
            )
            .first()
        )

        if existing_instrument is not None:
            return {
                "error": "Instrument with this serial number already exists"
            }

        instrument = Instrument(
            name=instrument_data.name,
            manufacturer=instrument_data.manufacturer,
            model=instrument_data.model,
            serial_number=instrument_data.serial_number,
            instrument_type=instrument_data.instrument_type,
            status="active"
        )

        db.add(instrument)
        db.commit()
        db.refresh(instrument)

        return {
            "message": "Instrument created successfully",
            "instrument_id": instrument.instrument_id,
            "name": instrument.name,
            "manufacturer": instrument.manufacturer,
            "model": instrument.model,
            "serial_number": instrument.serial_number,
            "instrument_type": instrument.instrument_type,
            "status": instrument.status
        }

    except Exception:

        db.rollback()

        return {
            "error": "Failed to create instrument"
        }

    finally:

        db.close()


# ============================================================
# CREATE CALIBRATION
# ============================================================

@app.post("/calibrations")
def create_calibration(
    calibration_data: CalibrationCreate
):

    # --------------------------------------------------------
    # Build model input
    # --------------------------------------------------------

    sensor_data = pd.DataFrame(
        [
            {
                "PT08.S1(CO)": calibration_data.sensor_1,
                "PT08.S2(NMHC)": calibration_data.sensor_2,
                "PT08.S3(NOx)": calibration_data.sensor_3,
                "PT08.S4(NO2)": calibration_data.sensor_4,
                "PT08.S5(O3)": calibration_data.sensor_5,
                "T": calibration_data.temperature,
                "RH": calibration_data.humidity,
                "AH": calibration_data.absolute_humidity
            }
        ]
    )

    # --------------------------------------------------------
    # Generate prediction
    # --------------------------------------------------------

    prediction = model.predict(sensor_data)[0]

    estimated_value = max(
        0.0,
        float(prediction)
    )

    # --------------------------------------------------------
    # Validate instrument
    # --------------------------------------------------------

    db = SessionLocal()

    try:

        instrument = (
            db.query(Instrument)
            .filter(
                Instrument.instrument_id
                == calibration_data.instrument_id
            )
            .first()
        )

        if instrument is None:
            return {
                "error": "Instrument not found"
            }

        if instrument.status != "active":
            return {
                "error": "Instrument is inactive"
            }

    finally:

        db.close()

    # --------------------------------------------------------
    # Save calibration
    # --------------------------------------------------------

    try:

        record = save_calibration(
            instrument_id=calibration_data.instrument_id,
            model_version=MODEL_VERSION,
            estimated_value=estimated_value,
            reference_value=calibration_data.reference_value,
            tolerance=calibration_data.tolerance
        )

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    # --------------------------------------------------------
    # Response
    # --------------------------------------------------------

    return {
        "message": "Calibration completed successfully",
        "record_id": record.record_id,
        "instrument_id": record.instrument_id,
        "estimated_value": record.estimated_value,
        "reference_value": record.reference_value,
        "error": record.error,
        "tolerance": record.tolerance,
        "status": record.status,
        "model_version": record.model_version
    }


# ============================================================
# GET ALL CALIBRATIONS
# ============================================================

@app.get("/calibrations")
def get_calibrations():

    db = SessionLocal()

    try:

        records = db.query(CalibrationRecord).all()

        return [
            {
                "record_id": record.record_id,
                "instrument_id": record.instrument_id,
                "measurement_time": record.measurement_time,
                "model_version": record.model_version,
                "estimated_value": record.estimated_value,
                "reference_value": record.reference_value,
                "error": record.error,
                "tolerance": record.tolerance,
                "status": record.status
            }
            for record in records
        ]

    finally:

        db.close()


# ============================================================
# GET SINGLE CALIBRATION
# ============================================================

@app.get("/calibrations/{record_id}")
def get_calibration(record_id: int):

    db = SessionLocal()

    try:

        record = (
            db.query(CalibrationRecord)
            .filter(
                CalibrationRecord.record_id == record_id
            )
            .first()
        )

        if record is None:
            return {
                "error": "Calibration record not found"
            }

        return {
            "record_id": record.record_id,
            "instrument_id": record.instrument_id,
            "measurement_time": record.measurement_time,
            "model_version": record.model_version,
            "estimated_value": record.estimated_value,
            "reference_value": record.reference_value,
            "error": record.error,
            "tolerance": record.tolerance,
            "status": record.status
        }

    finally:

        db.close()


# ============================================================
# GET INSTRUMENT CALIBRATIONS
# ============================================================

@app.get("/instruments/{instrument_id}/calibrations")
def get_instrument_calibrations(
    instrument_id: int
):

    db = SessionLocal()

    try:

        records = (
            db.query(CalibrationRecord)
            .filter(
                CalibrationRecord.instrument_id
                == instrument_id
            )
            .all()
        )

        return [
            {
                "record_id": record.record_id,
                "instrument_id": record.instrument_id,
                "measurement_time": record.measurement_time,
                "model_version": record.model_version,
                "estimated_value": record.estimated_value,
                "reference_value": record.reference_value,
                "error": record.error,
                "tolerance": record.tolerance,
                "status": record.status
            }
            for record in records
        ]

    finally:

        db.close()


# ============================================================
# LATEST CALIBRATION
# ============================================================

@app.get("/instruments/{instrument_id}/calibrations/latest")
def get_latest_calibration(
    instrument_id: int
):

    db = SessionLocal()

    try:

        record = (
            db.query(CalibrationRecord)
            .filter(
                CalibrationRecord.instrument_id
                == instrument_id
            )
            .order_by(
                CalibrationRecord.measurement_time.desc()
            )
            .first()
        )

        if record is None:
            return {
                "error": "No calibration records found"
            }

        return {
            "record_id": record.record_id,
            "instrument_id": record.instrument_id,
            "measurement_time": record.measurement_time,
            "model_version": record.model_version,
            "estimated_value": record.estimated_value,
            "reference_value": record.reference_value,
            "error": record.error,
            "tolerance": record.tolerance,
            "status": record.status
        }

    finally:

        db.close()


# ============================================================
# CALIBRATION SUMMARY
# ============================================================

@app.get("/instruments/{instrument_id}/calibration-summary")
def get_calibration_summary(
    instrument_id: int
):

    db = SessionLocal()

    try:

        records = (
            db.query(CalibrationRecord)
            .filter(
                CalibrationRecord.instrument_id
                == instrument_id
            )
            .all()
        )

        total = len(records)

        passed = sum(
            1
            for record in records
            if record.status == "PASS"
        )

        failed = sum(
            1
            for record in records
            if record.status == "FAIL"
        )

        return {
            "instrument_id": instrument_id,
            "total_calibrations": total,
            "passed": passed,
            "failed": failed
        }

    finally:

        db.close()


# ============================================================
# UPDATE INSTRUMENT STATUS
# ============================================================

@app.patch("/instruments/{instrument_id}/status")
def update_instrument_status(
    instrument_id: int,
    status: str
):

    db = SessionLocal()

    try:

        instrument = (
            db.query(Instrument)
            .filter(
                Instrument.instrument_id
                == instrument_id
            )
            .first()
        )

        if instrument is None:
            return {
                "error": "Instrument not found"
            }

        if status not in ["active", "inactive"]:
            return {
                "error": "Status must be 'active' or 'inactive'"
            }

        instrument.status = status

        db.commit()
        db.refresh(instrument)

        return {
            "message": "Instrument status updated",
            "instrument_id": instrument.instrument_id,
            "status": instrument.status
        }

    except Exception:

        db.rollback()

        return {
            "error": "Failed to update instrument status"
        }

    finally:

        db.close()


# ============================================================
# DELETE INSTRUMENT
# ============================================================

@app.delete("/instruments/{instrument_id}")
def delete_instrument(
    instrument_id: int
):

    db = SessionLocal()

    try:

        instrument = (
            db.query(Instrument)
            .filter(
                Instrument.instrument_id
                == instrument_id
            )
            .first()
        )

        if instrument is None:
            return {
                "error": "Instrument not found"
            }

        db.delete(instrument)
        db.commit()

        return {
            "message": "Instrument deleted successfully",
            "instrument_id": instrument_id
        }

    except Exception:

        db.rollback()

        return {
            "error": "Failed to delete instrument"
        }

    finally:

        db.close()


# ============================================================
# DELETE CALIBRATION
# ============================================================

@app.delete("/calibrations/{record_id}")
def delete_calibration(
    record_id: int
):

    db = SessionLocal()

    try:

        record = (
            db.query(CalibrationRecord)
            .filter(
                CalibrationRecord.record_id
                == record_id
            )
            .first()
        )

        if record is None:
            return {
                "error": "Calibration record not found"
            }

        db.delete(record)
        db.commit()

        return {
            "message": "Calibration record deleted successfully",
            "record_id": record_id
        }

    except Exception:

        db.rollback()

        return {
            "error": "Failed to delete calibration record"
        }

    finally:

        db.close()


# ============================================================
# CALIBRATIONS BY STATUS
# ============================================================

@app.get("/calibrations/status/{status}")
def get_calibrations_by_status(
    status: str
):

    if status.upper() not in ["PASS", "FAIL"]:
        return {
            "error": "Status must be PASS or FAIL"
        }

    db = SessionLocal()

    try:

        records = (
            db.query(CalibrationRecord)
            .filter(
                CalibrationRecord.status
                == status.upper()
            )
            .all()
        )

        return [
            {
                "record_id": record.record_id,
                "instrument_id": record.instrument_id,
                "measurement_time": record.measurement_time,
                "model_version": record.model_version,
                "estimated_value": record.estimated_value,
                "reference_value": record.reference_value,
                "error": record.error,
                "tolerance": record.tolerance,
                "status": record.status
            }
            for record in records
        ]

    finally:

        db.close()


# ============================================================
# INSTRUMENT CALIBRATION STATISTICS
# ============================================================

@app.get("/instruments/{instrument_id}/calibration-statistics")
def get_calibration_statistics(
    instrument_id: int
):

    db = SessionLocal()

    try:

        records = (
            db.query(CalibrationRecord)
            .filter(
                CalibrationRecord.instrument_id
                == instrument_id
            )
            .all()
        )

        if not records:
            return {
                "error": "No calibration records found"
            }

        errors = [
            record.error
            for record in records
            if record.error is not None
        ]

        absolute_errors = [
            abs(error)
            for error in errors
        ]

        mean_error = (
            sum(errors) / len(errors)
        )

        mean_absolute_error = (
            sum(absolute_errors)
            / len(absolute_errors)
        )

        return {
            "instrument_id": instrument_id,
            "total_calibrations": len(records),
            "mean_error": mean_error,
            "mean_absolute_error": mean_absolute_error,
            "maximum_absolute_error": max(
                absolute_errors
            ),
            "minimum_absolute_error": min(
                absolute_errors
            )
        }

    finally:

        db.close()


# ============================================================
# CALIBRATION HISTORY
# ============================================================

@app.get("/instruments/{instrument_id}/calibrations/history")
def get_calibration_history(
    instrument_id: int,
    limit: int = 10
):

    if limit < 1:
        return {
            "error": "Limit must be greater than 0"
        }

    db = SessionLocal()

    try:

        records = (
            db.query(CalibrationRecord)
            .filter(
                CalibrationRecord.instrument_id
                == instrument_id
            )
            .order_by(
                CalibrationRecord.measurement_time.desc()
            )
            .limit(limit)
            .all()
        )

        return [
            {
                "record_id": record.record_id,
                "instrument_id": record.instrument_id,
                "measurement_time": record.measurement_time,
                "model_version": record.model_version,
                "estimated_value": record.estimated_value,
                "reference_value": record.reference_value,
                "error": record.error,
                "tolerance": record.tolerance,
                "status": record.status
            }
            for record in records
        ]

    finally:

        db.close()


# ============================================================
# SYSTEM STATUS
# ============================================================

@app.get("/system/status")
def get_system_status():

    db_status = "healthy"
    model_status = "loaded"

    db = SessionLocal()

    try:

        db.execute(text("SELECT 1"))

    except Exception:

        db_status = "error"

    finally:

        db.close()

    if model is None:
        model_status = "not loaded"

    return {
        "api": "healthy",
        "database": db_status,
        "ml_model": model_status,
        "model_version": MODEL_VERSION
    }


# ============================================================
# CALIBRATION SCHEDULE
# ============================================================

@app.get("/calibration-schedule/due")
def get_due_calibrations(
    days: int = 30
):

    if days < 1:
        return {
            "error": "Days must be greater than 0"
        }

    return {
        "days": days,
        "due_instruments": get_due_instruments(days)
    }


# ============================================================
# ALL CALIBRATION STATISTICS
# ============================================================

@app.get("/calibration-statistics")
def get_all_calibration_statistics():

    db = SessionLocal()

    try:

        records = db.query(CalibrationRecord).all()

        if not records:
            return {
                "total_calibrations": 0,
                "mean_error": 0,
                "mean_absolute_error": 0,
                "max_absolute_error": 0,
                "min_absolute_error": 0
            }

        errors = [
            record.error
            for record in records
            if record.error is not None
        ]

        if not errors:
            return {
                "total_calibrations": len(records),
                "mean_error": 0,
                "mean_absolute_error": 0,
                "max_absolute_error": 0,
                "min_absolute_error": 0
            }

        absolute_errors = [
            abs(error)
            for error in errors
        ]

        return {
            "total_calibrations": len(records),
            "mean_error": (
                sum(errors)
                / len(errors)
            ),
            "mean_absolute_error": (
                sum(absolute_errors)
                / len(absolute_errors)
            ),
            "max_absolute_error": max(
                absolute_errors
            ),
            "min_absolute_error": min(
                absolute_errors
            )
        }

    finally:

        db.close()