"""
Lab Calibration System - V6

Main FastAPI application entry point.
"""

from src.v5.database.database import SessionLocal
from src.v5.database.models import (
    Instrument,
    InstrumentConfiguration,
    CalibrationPolicy,
    Model,
)
from fastapi.responses import Response

from src.v3.calibration_report import generate_calibration_report
from src.v5.database.models import Instrument, CalibrationRecord
from src.v5.database.database import SessionLocal



from src.v5.services.configuration_service import (
    get_instrument_configurations,
)
from src.v5.services.policy_service import (
    get_instrument_policies,
)
from src.v5.registry.model_registry import (
    get_approved_models,
)

from src.v6.api.calibration_history import (
    get_instrument_calibration_history,
)

from src.v6.api.calibration_summary import (
    get_calibration_summary,
)


from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from uuid import uuid4

from src.v6.hardware.calibration_orchestrator import (
    CalibrationOrchestrator,
)
from src.v6.hardware.calibration_pair import CalibrationPair
from src.v6.hardware.driver_registry import (
    create_instrument_driver,
)
from src.v6.hardware.hardware_in_loop import (
    HardwareInLoopController,
)
from src.v6.hardware.hardware_session import (
    HardwareSession,
)
from src.v6.hardware.simulator.simulated_reference_standard import (
    SimulatedReferenceStandard,
)


app = FastAPI(
    title="Lab Calibration System - V6",
    version="6.0.0",
    description=(
        "Hardware-integrated calibration platform with "
        "instrument abstraction, acquisition, reference "
        "validation, safety, fault recovery, and "
        "calibration orchestration."
    ),
)


SESSIONS = {}


class HardwareSessionCreate(BaseModel):
    driver_type: str
    instrument_id: int
    model_id: int
    reference_value: float
    driver_config: dict = Field(default_factory=dict)


class CalibrationResponse(BaseModel):
    session_id: str
    record_id: int
    estimated_value: float
    reference_value: float
    status: str


@app.get("/")
def root():
    return {
        "name": "Lab Calibration System",
        "version": "6.0.0",
        "status": "running",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "version": "6.0.0",
    }


@app.get("/hardware/drivers")
def get_drivers():
    return {
        "drivers": [
            "simulated",
            "serial",
            "usb",
            "tcp",
        ]
    }


@app.post("/hardware/sessions")
def create_hardware_session(
    request: HardwareSessionCreate,
):
    if request.instrument_id < 1:
        raise HTTPException(
            status_code=400,
            detail="instrument_id must be greater than 0.",
        )

    if request.model_id < 1:
        raise HTTPException(
            status_code=400,
            detail="model_id must be greater than 0.",
        )

    if request.reference_value <= 0:
        raise HTTPException(
            status_code=400,
            detail="reference_value must be greater than 0.",
        )

    try:
        connection = dict(request.driver_config)

        if request.driver_type.lower() == "simulated":
            connection.setdefault(
                "instrument_id",
                request.instrument_id,
            )

        instrument = create_instrument_driver(
            request.driver_type,
            **connection,
        )

        reference = SimulatedReferenceStandard(
            request.reference_value
        )

        pair = CalibrationPair(
            instrument=instrument,
            reference=reference,
        )

        controller = HardwareInLoopController(
            pair=pair,
            instrument_id=request.instrument_id,
            model_id=request.model_id,
        )

        session = HardwareSession(controller)

        orchestrator = CalibrationOrchestrator(
            controller
        )

        session_id = str(uuid4())

        SESSIONS[session_id] = {
            "session": session,
            "orchestrator": orchestrator,
            "driver_type": request.driver_type.lower(),
            "instrument_id": request.instrument_id,
            "model_id": request.model_id,
        }

        return {
            "session_id": session_id,
            "driver_type": request.driver_type.lower(),
            "instrument_id": request.instrument_id,
            "model_id": request.model_id,
            "status": "created",
            "ready": session.is_ready(),
        }

    except (ValueError, TypeError) as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@app.get("/hardware/sessions/{session_id}")
def get_hardware_session(session_id: str):
    data = SESSIONS.get(session_id)

    if data is None:
        raise HTTPException(
            status_code=404,
            detail="Hardware session not found.",
        )

    session = data["session"]

    return {
        "session_id": session_id,
        "driver_type": data["driver_type"],
        "instrument_id": data["instrument_id"],
        "model_id": data["model_id"],
        "ready": session.is_ready(),
    }


@app.post("/hardware/sessions/{session_id}/start")
def start_hardware_session(session_id: str):
    data = SESSIONS.get(session_id)

    if data is None:
        raise HTTPException(
            status_code=404,
            detail="Hardware session not found.",
        )

    session = data["session"]

    try:
        session.start()

        return {
            "session_id": session_id,
            "status": "started",
            "ready": session.is_ready(),
        }

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@app.post(
    "/hardware/sessions/{session_id}/calibrate",
    response_model=CalibrationResponse,
)
def calibrate_hardware_session(session_id: str):
    data = SESSIONS.get(session_id)

    if data is None:
        raise HTTPException(
            status_code=404,
            detail="Hardware session not found.",
        )

    session = data["session"]

    try:
        calibration = session.run_calibration()

        return CalibrationResponse(
            session_id=session_id,
            record_id=calibration.record_id,
            estimated_value=calibration.estimated_value,
            reference_value=calibration.reference_value,
            status=calibration.status,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@app.post("/hardware/sessions/{session_id}/run")
def run_hardware_session(
    session_id: str,
    number_of_cycles: int = 5,
    interval_seconds: float = 1.0,
):
    data = SESSIONS.get(session_id)

    if data is None:
        raise HTTPException(
            status_code=404,
            detail="Hardware session not found.",
        )

    if number_of_cycles <= 0:
        raise HTTPException(
            status_code=400,
            detail="number_of_cycles must be greater than 0.",
        )

    if interval_seconds < 0:
        raise HTTPException(
            status_code=400,
            detail="interval_seconds cannot be negative.",
        )

    session = data["session"]
    orchestrator = data["orchestrator"]

    if not session.is_ready():
        raise HTTPException(
            status_code=400,
            detail="Hardware session is not ready.",
        )

    try:
        results = orchestrator.run(
            number_of_cycles=number_of_cycles,
            interval_seconds=interval_seconds,
        )

        return {
            "session_id": session_id,
            "cycles_requested": number_of_cycles,
            "cycles_completed": len(results),
            "results": [
                {
                    "record_id": result.record_id,
                    "estimated_value": result.estimated_value,
                    "reference_value": result.reference_value,
                    "status": result.status,
                }
                for result in results
            ],
        }

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@app.post("/hardware/sessions/{session_id}/stop")
def stop_hardware_session(session_id: str):
    data = SESSIONS.get(session_id)

    if data is None:
        raise HTTPException(
            status_code=404,
            detail="Hardware session not found.",
        )

    session = data["session"]

    session.stop()

    return {
        "session_id": session_id,
        "status": "stopped",
        "ready": session.is_ready(),
    }


@app.delete("/hardware/sessions/{session_id}")
def delete_hardware_session(session_id: str):
    data = SESSIONS.get(session_id)

    if data is None:
        raise HTTPException(
            status_code=404,
            detail="Hardware session not found.",
        )

    session = data["session"]

    session.stop()

    del SESSIONS[session_id]

    return {
        "session_id": session_id,
        "status": "deleted",
    }


@app.get(
    "/hardware/instruments/{instrument_id}/calibrations"
)
def get_calibration_history(
    instrument_id: int,
    limit: int = 100,
):
    try:
        records = get_instrument_calibration_history(
            instrument_id=instrument_id,
            limit=limit,
        )

        return {
            "instrument_id": instrument_id,
            "count": len(records),
            "records": [
                {
                    "record_id": record.record_id,
                    "model_id": record.model_id,
                    "measurement_id": record.measurement_id,
                    "measurement_time": (
                        record.measurement_time.isoformat()
                        if record.measurement_time
                        else None
                    ),
                    "estimated_value": record.estimated_value,
                    "reference_value": record.reference_value,
                    "error": record.error,
                    "absolute_error": record.absolute_error,
                    "tolerance": record.tolerance,
                    "status": record.status,
                    "created_at": (
                        record.created_at.isoformat()
                        if record.created_at
                        else None
                    ),
                }
                for record in records
            ],
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@app.get(
    "/hardware/instruments/{instrument_id}/calibration-summary"
)
def calibration_summary(instrument_id: int):
    try:
        return get_calibration_summary(
            instrument_id=instrument_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

# ============================================================
# V5 MANAGEMENT API
# ============================================================

@app.get("/instruments")
def get_instruments():
    db = SessionLocal()

    try:
        instruments = (
            db.query(Instrument)
            .order_by(Instrument.instrument_id)
            .all()
        )

        return {
            "count": len(instruments),
            "instruments": [
                {
                    "instrument_id": instrument.instrument_id,
                    "name": instrument.name,
                    "manufacturer": instrument.manufacturer,
                    "model": instrument.model,
                    "serial_number": instrument.serial_number,
                    "instrument_type": instrument.instrument_type,
                    "status": instrument.status,
                    "created_at": (
                        instrument.created_at.isoformat()
                        if instrument.created_at
                        else None
                    ),
                }
                for instrument in instruments
            ],
        }

    finally:
        db.close()


@app.get("/instruments/{instrument_id}")
def get_instrument(instrument_id: int):
    if instrument_id < 1:
        raise HTTPException(
            status_code=400,
            detail="instrument_id must be greater than 0.",
        )

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
            raise HTTPException(
                status_code=404,
                detail="Instrument not found.",
            )

        return {
            "instrument_id": instrument.instrument_id,
            "name": instrument.name,
            "manufacturer": instrument.manufacturer,
            "model": instrument.model,
            "serial_number": instrument.serial_number,
            "instrument_type": instrument.instrument_type,
            "status": instrument.status,
            "created_at": (
                instrument.created_at.isoformat()
                if instrument.created_at
                else None
            ),
        }

    finally:
        db.close()


@app.get("/instruments/{instrument_id}/configurations")
def get_instrument_configurations_api(
    instrument_id: int,
):
    if instrument_id < 1:
        raise HTTPException(
            status_code=400,
            detail="instrument_id must be greater than 0.",
        )

    try:
        configurations = get_instrument_configurations(
            instrument_id
        )

        return {
            "instrument_id": instrument_id,
            "count": len(configurations),
            "configurations": [
                {
                    "configuration_id": configuration.configuration_id,
                    "configuration_name": (
                        configuration.configuration_name
                    ),
                    "input_schema": configuration.input_schema,
                    "target_variable": (
                        configuration.target_variable
                    ),
                    "unit": configuration.unit,
                    "active": configuration.active,
                    "created_at": (
                        configuration.created_at.isoformat()
                        if configuration.created_at
                        else None
                    ),
                    "updated_at": (
                        configuration.updated_at.isoformat()
                        if configuration.updated_at
                        else None
                    ),
                }
                for configuration in configurations
            ],
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@app.get("/instruments/{instrument_id}/policies")
def get_instrument_policies_api(
    instrument_id: int,
):
    if instrument_id < 1:
        raise HTTPException(
            status_code=400,
            detail="instrument_id must be greater than 0.",
        )

    try:
        policies = get_instrument_policies(
            instrument_id
        )

        return {
            "instrument_id": instrument_id,
            "count": len(policies),
            "policies": [
                {
                    "policy_id": policy.policy_id,
                    "calibration_interval_days": (
                        policy.calibration_interval_days
                    ),
                    "tolerance": policy.tolerance,
                    "reference_required": (
                        policy.reference_required
                    ),
                    "active": policy.active,
                    "created_at": (
                        policy.created_at.isoformat()
                        if policy.created_at
                        else None
                    ),
                    "updated_at": (
                        policy.updated_at.isoformat()
                        if policy.updated_at
                        else None
                    ),
                }
                for policy in policies
            ],
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@app.get("/models")
def get_models():
    db = SessionLocal()

    try:
        models = (
            db.query(Model)
            .order_by(Model.model_id)
            .all()
        )

        return {
            "count": len(models),
            "models": [
                {
                    "model_id": model.model_id,
                    "model_name": model.model_name,
                    "model_version": model.model_version,
                    "instrument_type": model.instrument_type,
                    "target_variable": model.target_variable,
                    "framework": model.framework,
                    "artifact_path": model.artifact_path,
                    "artifact_hash": model.artifact_hash,
                    "status": model.status,
                    "created_at": (
                        model.created_at.isoformat()
                        if model.created_at
                        else None
                    ),
                }
                for model in models
            ],
        }

    finally:
        db.close()


@app.get("/models/approved")
def get_approved_models_api():
    models = get_approved_models()

    return {
        "count": len(models),
        "models": [
            {
                "model_id": model.model_id,
                "model_name": model.model_name,
                "model_version": model.model_version,
                "instrument_type": model.instrument_type,
                "target_variable": model.target_variable,
                "framework": model.framework,
                "status": model.status,
                "created_at": (
                    model.created_at.isoformat()
                    if model.created_at
                    else None
                ),
            }
            for model in models
        ],
    }



# ============================================================
# CALIBRATION PDF REPORT
# ============================================================
# ============================================================
# CALIBRATION PDF REPORT
# ============================================================

@app.get("/instruments/{instrument_id}/calibrations/{record_id}/report")
def download_calibration_report(
    instrument_id: int,
    record_id: int,
):
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
            raise HTTPException(
                status_code=404,
                detail="Instrument not found.",
            )

        record = (
            db.query(CalibrationRecord)
            .filter(
                CalibrationRecord.record_id == record_id,
                CalibrationRecord.instrument_id == instrument_id,
            )
            .first()
        )

        if record is None:
            raise HTTPException(
                status_code=404,
                detail="Calibration record not found for this instrument.",
            )

        records = (
            db.query(CalibrationRecord)
            .filter(
                CalibrationRecord.instrument_id == instrument_id
            )
            .all()
        )

        errors = [
            item.error
            for item in records
            if item.error is not None
        ]

        absolute_errors = [
            abs(error)
            for error in errors
        ]

        pass_count = sum(
            1
            for item in records
            if item.status == "PASS"
        )

        fail_count = sum(
            1
            for item in records
            if item.status == "FAIL"
        )

        count = len(records)

        statistics = {
            "count": count,
            "pass_count": pass_count,
            "fail_count": fail_count,
            "pass_rate": (
                (pass_count / count) * 100
                if count
                else 0
            ),
            "mae": (
                sum(absolute_errors) / len(absolute_errors)
                if absolute_errors
                else 0
            ),
            "average_error": (
                sum(errors) / len(errors)
                if errors
                else 0
            ),
            "maximum_absolute_error": (
                max(absolute_errors)
                if absolute_errors
                else 0
            ),
        }

        # V5 stores model information through the relationship.
        # V3 report generation expects model_version directly.
        if record.model is not None:
            record.model_version = record.model.model_version
        else:
            record.model_version = "unknown"

        pdf_bytes = generate_calibration_report(
            instrument=instrument,
            record=record,
            statistics=statistics,
        )

        filename = (
            f"calibration_report_"
            f"{instrument.serial_number}_"
            f"record_{record.record_id}.pdf"
        )

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": (
                    f'attachment; filename="{filename}"'
                )
            },
        )

    finally:
        db.close()
