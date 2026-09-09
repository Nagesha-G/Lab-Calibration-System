from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.v6.hardware.calibration_orchestrator import CalibrationOrchestrator
from src.v6.hardware.calibration_pair import CalibrationPair
from src.v6.hardware.driver_registry import create_instrument_driver
from src.v6.hardware.hardware_in_loop import HardwareInLoopController
from src.v6.hardware.hardware_session import HardwareSession
from src.v6.hardware.simulator.simulated_reference_standard import (
    SimulatedReferenceStandard,
)


app = FastAPI(
    title="V6 Hardware Integration API",
    version="1.0.0",
    description=(
        "Hardware control and calibration orchestration API."
    ),
)


SESSIONS = {}


class HardwareSessionCreate(BaseModel):
    driver_type: str
    instrument_id: int
    model_id: int
    reference_value: float
    driver_config: dict = {}


class CalibrationResponse(BaseModel):
    session_id: str
    record_id: int
    estimated_value: float
    reference_value: float
    status: str


@app.get("/")
def root():
    return {
        "name": "V6 Hardware Integration API",
        "version": "1.0.0",
        "status": "running",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


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
        instrument = create_instrument_driver(
            request.driver_type,
            **request.driver_config,
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

        session_id = str(uuid4())

        SESSIONS[session_id] = {
            "session": session,
            "orchestrator": CalibrationOrchestrator(
                controller
            ),
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