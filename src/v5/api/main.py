from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel
from sqlalchemy import text

from src.v5.database.database import SessionLocal
from src.v5.database.models import Instrument

from src.v5.services.configuration_service import (
    create_configuration,
    get_configuration,
    get_instrument_configurations,
    get_active_configuration,
)

from src.v5.registry.model_registry import (
    register_model,
    get_model,
    get_approved_models,
)

from src.v5.services.policy_service import (
    create_policy,
    get_policy,
    get_instrument_policies,
    get_active_policy,
    calculate_next_calibration_date,
    get_calibration_status,
)

from src.v5.services.measurement_service import (
    create_measurement,
    get_measurement,
    get_instrument_measurements,
    parse_measurement_data,
)


from src.v5.services.calibration_engine import (
    run_calibration,
)

from src.v5.services.audit_service import (
    create_audit_log,
    get_audit_log,
    get_entity_audit_logs,
    get_user_audit_logs,
)

from src.v5.services.user_service import (
    create_user,
    get_user,
    authenticate_user,
    deactivate_user,
)


from src.v5.services.user_service import (
    create_user,
    get_user,
    authenticate_user,
    deactivate_user,
)


app = FastAPI(
    title="V5 Calibration Intelligence Platform",
    version="5.0.0",
    description=(
        "Multi-instrument calibration management and "
        "calibration intelligence platform."
    ),
)


# =========================================================
# PYDANTIC REQUEST MODELS
# =========================================================

class InstrumentCreate(BaseModel):
    name: str
    manufacturer: str
    model: str
    serial_number: str
    instrument_type: str


class InstrumentStatusUpdate(BaseModel):
    status: str


class ConfigurationCreate(BaseModel):
    instrument_id: int
    configuration_name: str
    input_schema: dict
    target_variable: str
    unit: str
    active: bool = True


class ModelRegisterRequest(BaseModel):
    model_name: str
    model_version: str
    instrument_type: str
    target_variable: str
    framework: str
    artifact_path: str
    status: str = "registered"

class CalibrationPolicyCreate(BaseModel):
    instrument_id: int
    calibration_interval_days: int
    tolerance: float
    reference_required: bool = True
    active: bool = True

class MeasurementCreate(BaseModel):
    instrument_id: int
    measurement_data: dict


class CalibrationRequest(BaseModel):
    instrument_id: int
    measurement_id: int
    model_id: int
    reference_value: float

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: str = "operator"


class AuditLogCreate(BaseModel):
    user_id: int | None = None
    action: str
    entity_type: str
    entity_id: int
    details: str | None = None


class UserLogin(BaseModel):
    username: str
    password: str

# =========================================================
# AUTHENTICATION HELPERS
# =========================================================

# =========================================================
# AUTHENTICATION HELPERS
# =========================================================

def get_authenticated_user(
    username: str | None = Header(default=None),
    password: str | None = Header(default=None),
):
    if not username or not password:
        raise HTTPException(
            status_code=401,
            detail="Authentication required.",
        )

    user = authenticate_user(
        username=username,
        password=password,
    )

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password.",
        )

    return user


def require_admin(
    user=Depends(get_authenticated_user),
):
    if user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Administrator access required.",
        )

    return user

# =========================================================
# ROOT / HEALTH
# =========================================================

@app.get("/")
def root():
    return {
        "name": "V5 Calibration Intelligence Platform",
        "version": "5.0.0",
        "status": "running",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
    }


@app.get("/system/status")
def system_status():
    db = SessionLocal()

    try:
        db.execute(text("SELECT 1"))

        return {
            "status": "healthy",
            "database": "connected",
            "api_version": "5.0.0",
        }

    except Exception as exc:
        return {
            "status": "unhealthy",
            "database": "error",
            "error": str(exc),
            "api_version": "5.0.0",
        }

    finally:
        db.close()


# =========================================================
# INSTRUMENT API
# =========================================================

@app.post("/instruments")
def create_instrument(
    request: InstrumentCreate,
):
    db = SessionLocal()

    try:
        if not request.name.strip():
            raise HTTPException(
                status_code=400,
                detail="Instrument name cannot be empty.",
            )

        if not request.manufacturer.strip():
            raise HTTPException(
                status_code=400,
                detail="Manufacturer cannot be empty.",
            )

        if not request.model.strip():
            raise HTTPException(
                status_code=400,
                detail="Model cannot be empty.",
            )

        if not request.serial_number.strip():
            raise HTTPException(
                status_code=400,
                detail="Serial number cannot be empty.",
            )

        if not request.instrument_type.strip():
            raise HTTPException(
                status_code=400,
                detail="Instrument type cannot be empty.",
            )

        existing = (
            db.query(Instrument)
            .filter(
                Instrument.serial_number
                == request.serial_number
            )
            .first()
        )

        if existing is not None:
            raise HTTPException(
                status_code=409,
                detail="Serial number already exists.",
            )

        instrument = Instrument(
            name=request.name,
            manufacturer=request.manufacturer,
            model=request.model,
            serial_number=request.serial_number,
            instrument_type=request.instrument_type,
            status="active",
        )

        db.add(instrument)
        db.commit()
        db.refresh(instrument)

        return {
            "instrument_id": instrument.instrument_id,
            "name": instrument.name,
            "manufacturer": instrument.manufacturer,
            "model": instrument.model,
            "serial_number": instrument.serial_number,
            "instrument_type": instrument.instrument_type,
            "status": instrument.status,
            "created_at": instrument.created_at,
        }

    except HTTPException:
        raise

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


@app.get("/instruments")
def get_instruments():
    db = SessionLocal()

    try:
        instruments = (
            db.query(Instrument)
            .order_by(
                Instrument.instrument_id
            )
            .all()
        )

        return [
            {
                "instrument_id": instrument.instrument_id,
                "name": instrument.name,
                "manufacturer": instrument.manufacturer,
                "model": instrument.model,
                "serial_number": instrument.serial_number,
                "instrument_type": instrument.instrument_type,
                "status": instrument.status,
                "created_at": instrument.created_at,
            }
            for instrument in instruments
        ]

    finally:
        db.close()


@app.get("/instruments/{instrument_id}")
def get_instrument(
    instrument_id: int,
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
            "created_at": instrument.created_at,
        }

    finally:
        db.close()


@app.patch("/instruments/{instrument_id}/status")
def update_instrument_status(
    instrument_id: int,
    request: InstrumentStatusUpdate,
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
            raise HTTPException(
                status_code=404,
                detail="Instrument not found.",
            )

        allowed_statuses = {
            "active",
            "inactive",
        }

        if request.status not in allowed_statuses:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Status must be either "
                    "'active' or 'inactive'."
                ),
            )

        instrument.status = request.status

        db.commit()
        db.refresh(instrument)

        return {
            "instrument_id": instrument.instrument_id,
            "status": instrument.status,
        }

    except HTTPException:
        raise

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


# =========================================================
# CONFIGURATION API
# =========================================================

@app.post("/configurations")
def create_instrument_configuration(
    request: ConfigurationCreate,
):
    try:
        configuration = create_configuration(
            instrument_id=request.instrument_id,
            configuration_name=request.configuration_name,
            input_schema=request.input_schema,
            target_variable=request.target_variable,
            unit=request.unit,
            active=request.active,
        )

        return {
            "configuration_id": (
                configuration.configuration_id
            ),
            "instrument_id": (
                configuration.instrument_id
            ),
            "configuration_name": (
                configuration.configuration_name
            ),
            "input_schema": request.input_schema,
            "target_variable": (
                configuration.target_variable
            ),
            "unit": configuration.unit,
            "active": configuration.active,
            "created_at": configuration.created_at,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


@app.get("/configurations/{configuration_id}")
def get_configuration_endpoint(
    configuration_id: int,
):
    configuration = get_configuration(
        configuration_id
    )

    if configuration is None:
        raise HTTPException(
            status_code=404,
            detail="Configuration not found.",
        )

    import json

    return {
        "configuration_id": (
            configuration.configuration_id
        ),
        "instrument_id": (
            configuration.instrument_id
        ),
        "configuration_name": (
            configuration.configuration_name
        ),
        "input_schema": json.loads(
            configuration.input_schema
        ),
        "target_variable": (
            configuration.target_variable
        ),
        "unit": configuration.unit,
        "active": configuration.active,
        "created_at": configuration.created_at,
    }


@app.get(
    "/instruments/{instrument_id}/configurations"
)
def get_instrument_configurations_endpoint(
    instrument_id: int,
):
    configurations = get_instrument_configurations(
        instrument_id
    )

    import json

    return [
        {
            "configuration_id": (
                configuration.configuration_id
            ),
            "instrument_id": (
                configuration.instrument_id
            ),
            "configuration_name": (
                configuration.configuration_name
            ),
            "input_schema": json.loads(
                configuration.input_schema
            ),
            "target_variable": (
                configuration.target_variable
            ),
            "unit": configuration.unit,
            "active": configuration.active,
            "created_at": configuration.created_at,
        }
        for configuration in configurations
    ]


@app.get(
    "/instruments/{instrument_id}/configurations/active"
)
def get_active_configuration_endpoint(
    instrument_id: int,
):
    configuration = get_active_configuration(
        instrument_id
    )

    if configuration is None:
        raise HTTPException(
            status_code=404,
            detail="Active configuration not found.",
        )

    import json

    return {
        "configuration_id": (
            configuration.configuration_id
        ),
        "instrument_id": (
            configuration.instrument_id
        ),
        "configuration_name": (
            configuration.configuration_name
        ),
        "input_schema": json.loads(
            configuration.input_schema
        ),
        "target_variable": (
            configuration.target_variable
        ),
        "unit": configuration.unit,
        "active": configuration.active,
        "created_at": configuration.created_at,
    }


# =========================================================
# MODEL REGISTRY API
# =========================================================

@app.post("/models")
def register_model_endpoint(
    request: ModelRegisterRequest,
):
    try:
        model = register_model(
            model_name=request.model_name,
            model_version=request.model_version,
            instrument_type=request.instrument_type,
            target_variable=request.target_variable,
            framework=request.framework,
            artifact_path=request.artifact_path,
            status=request.status,
        )

        return {
            "model_id": model.model_id,
            "model_name": model.model_name,
            "model_version": model.model_version,
            "instrument_type": model.instrument_type,
            "target_variable": model.target_variable,
            "framework": model.framework,
            "artifact_path": model.artifact_path,
            "artifact_hash": model.artifact_hash,
            "status": model.status,
            "created_at": model.created_at,
        }

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


# =========================================================
# MODEL REGISTRY API
# =========================================================

@app.post("/models")
def register_model_endpoint(
    request: ModelRegisterRequest,
):
    try:
        model = register_model(
            model_name=request.model_name,
            model_version=request.model_version,
            instrument_type=request.instrument_type,
            target_variable=request.target_variable,
            framework=request.framework,
            artifact_path=request.artifact_path,
            status=request.status,
        )

        return {
            "model_id": model.model_id,
            "model_name": model.model_name,
            "model_version": model.model_version,
            "instrument_type": model.instrument_type,
            "target_variable": model.target_variable,
            "framework": model.framework,
            "artifact_path": model.artifact_path,
            "artifact_hash": model.artifact_hash,
            "status": model.status,
            "created_at": model.created_at,
        }

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


@app.get("/models/approved")
def get_approved_models_endpoint():
    models = get_approved_models()

    return [
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
            "created_at": model.created_at,
        }
        for model in models
    ]


@app.get("/models/{model_id}")
def get_model_endpoint(
    model_id: int,
):
    model = get_model(model_id)

    if model is None:
        raise HTTPException(
            status_code=404,
            detail="Model not found.",
        )

    return {
        "model_id": model.model_id,
        "model_name": model.model_name,
        "model_version": model.model_version,
        "instrument_type": model.instrument_type,
        "target_variable": model.target_variable,
        "framework": model.framework,
        "artifact_path": model.artifact_path,
        "artifact_hash": model.artifact_hash,
        "status": model.status,
        "created_at": model.created_at,
    }


@app.get("/models/approved")
def get_approved_models_endpoint():
    models = get_approved_models()

    return [
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
            "created_at": model.created_at,
        }
        for model in models
    ]
@app.get("/models/{model_id}")
def get_model_endpoint(
    model_id: int,
):
    model = get_model(model_id)

    if model is None:
        raise HTTPException(
            status_code=404,
            detail="Model not found.",
        )

    return {
        "model_id": model.model_id,
        "model_name": model.model_name,
        "model_version": model.model_version,
        "instrument_type": model.instrument_type,
        "target_variable": model.target_variable,
        "framework": model.framework,
        "artifact_path": model.artifact_path,
        "artifact_hash": model.artifact_hash,
        "status": model.status,
        "created_at": model.created_at,
    }
    model = get_model(model_id)

    if model is None:
        raise HTTPException(
            status_code=404,
            detail="Model not found.",
        )
# =========================================================
# CALIBRATION POLICY API
# =========================================================

@app.post("/policies")
def create_calibration_policy(
    request: CalibrationPolicyCreate,
):
    try:
        policy = create_policy(
            instrument_id=request.instrument_id,
            calibration_interval_days=request.calibration_interval_days,
            tolerance=request.tolerance,
            reference_required=request.reference_required,
            active=request.active,
        )

        return {
            "policy_id": policy.policy_id,
            "instrument_id": policy.instrument_id,
            "calibration_interval_days": (
                policy.calibration_interval_days
            ),
            "tolerance": policy.tolerance,
            "reference_required": policy.reference_required,
            "active": policy.active,
            "created_at": policy.created_at,
            "updated_at": policy.updated_at,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


@app.get("/policies/{policy_id}")
def get_calibration_policy(
    policy_id: int,
):
    policy = get_policy(policy_id)

    if policy is None:
        raise HTTPException(
            status_code=404,
            detail="Calibration policy not found.",
        )

    return {
        "policy_id": policy.policy_id,
        "instrument_id": policy.instrument_id,
        "calibration_interval_days": (
            policy.calibration_interval_days
        ),
        "tolerance": policy.tolerance,
        "reference_required": policy.reference_required,
        "active": policy.active,
        "created_at": policy.created_at,
        "updated_at": policy.updated_at,
    }


@app.get("/instruments/{instrument_id}/policies")
def get_instrument_calibration_policies(
    instrument_id: int,
):
    policies = get_instrument_policies(instrument_id)

    return [
        {
            "policy_id": policy.policy_id,
            "instrument_id": policy.instrument_id,
            "calibration_interval_days": (
                policy.calibration_interval_days
            ),
            "tolerance": policy.tolerance,
            "reference_required": policy.reference_required,
            "active": policy.active,
            "created_at": policy.created_at,
            "updated_at": policy.updated_at,
        }
        for policy in policies
    ]


@app.get("/instruments/{instrument_id}/policies/active")
def get_active_calibration_policy(
    instrument_id: int,
):
    policy = get_active_policy(instrument_id)

    if policy is None:
        raise HTTPException(
            status_code=404,
            detail="Active calibration policy not found.",
        )

    return {
        "policy_id": policy.policy_id,
        "instrument_id": policy.instrument_id,
        "calibration_interval_days": (
            policy.calibration_interval_days
        ),
        "tolerance": policy.tolerance,
        "reference_required": policy.reference_required,
        "active": policy.active,
        "created_at": policy.created_at,
        "updated_at": policy.updated_at,
    }


# =========================================================
# MEASUREMENT API
# =========================================================

@app.post("/measurements")
def create_measurement_endpoint(
    request: MeasurementCreate,
):
    try:
        measurement = create_measurement(
            instrument_id=request.instrument_id,
            measurement_data=request.measurement_data,
        )

        return {
            "measurement_id": measurement.measurement_id,
            "instrument_id": measurement.instrument_id,
            "measurement_data": parse_measurement_data(
                measurement
            ),
            "created_at": measurement.created_at,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


@app.get("/measurements/{measurement_id}")
def get_measurement_endpoint(
    measurement_id: int,
):
    measurement = get_measurement(measurement_id)

    if measurement is None:
        raise HTTPException(
            status_code=404,
            detail="Measurement not found.",
        )

    return {
        "measurement_id": measurement.measurement_id,
        "instrument_id": measurement.instrument_id,
        "measurement_data": parse_measurement_data(
            measurement
        ),
        "created_at": measurement.created_at,
    }


@app.get("/instruments/{instrument_id}/measurements")
def get_instrument_measurements_endpoint(
    instrument_id: int,
):
    measurements = get_instrument_measurements(
        instrument_id
    )

    return [
        {
            "measurement_id": measurement.measurement_id,
            "instrument_id": measurement.instrument_id,
            "measurement_data": parse_measurement_data(
                measurement
            ),
            "created_at": measurement.created_at,
        }
        for measurement in measurements
    ]


# =========================================================
# CALIBRATION API
# =========================================================

@app.post("/calibrations")
def run_calibration_endpoint(
    request: CalibrationRequest,
):
    try:
        record = run_calibration(
            instrument_id=request.instrument_id,
            measurement_id=request.measurement_id,
            model_id=request.model_id,
            reference_value=request.reference_value,
        )

        return {
            "record_id": record.record_id,
            "instrument_id": record.instrument_id,
            "model_id": record.model_id,
            "measurement_id": record.measurement_id,
            "measurement_time": record.measurement_time,
            "estimated_value": record.estimated_value,
            "reference_value": record.reference_value,
            "error": record.error,
            "absolute_error": record.absolute_error,
            "tolerance": record.tolerance,
            "status": record.status,
            "created_at": record.created_at,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


@app.get("/calibrations/{record_id}")
def get_calibration_endpoint(
    record_id: int,
):
    from src.v5.database.database import SessionLocal
    from src.v5.database.models import CalibrationRecord

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
            raise HTTPException(
                status_code=404,
                detail="Calibration record not found.",
            )

        return {
            "record_id": record.record_id,
            "instrument_id": record.instrument_id,
            "model_id": record.model_id,
            "measurement_id": record.measurement_id,
            "measurement_time": record.measurement_time,
            "estimated_value": record.estimated_value,
            "reference_value": record.reference_value,
            "error": record.error,
            "absolute_error": record.absolute_error,
            "tolerance": record.tolerance,
            "status": record.status,
            "created_at": record.created_at,
        }

    finally:
        db.close()


@app.get("/instruments/{instrument_id}/calibrations")
def get_instrument_calibrations_endpoint(
    instrument_id: int,
):
    from src.v5.database.database import SessionLocal
    from src.v5.database.models import CalibrationRecord

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
            .all()
        )

        return [
            {
                "record_id": record.record_id,
                "instrument_id": record.instrument_id,
                "model_id": record.model_id,
                "measurement_id": record.measurement_id,
                "measurement_time": record.measurement_time,
                "estimated_value": record.estimated_value,
                "reference_value": record.reference_value,
                "error": record.error,
                "absolute_error": record.absolute_error,
                "tolerance": record.tolerance,
                "status": record.status,
                "created_at": record.created_at,
            }
            for record in records
        ]

    finally:
        db.close()

# =========================================================
# USER API
# =========================================================

@app.post("/users")
def create_user_endpoint(
    request: UserCreate,
):
    try:
        user = create_user(
            username=request.username,
            email=request.email,
            password=request.password,
            role=request.role,
        )

        return {
            "user_id": user.user_id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "status": user.status,
            "created_at": user.created_at,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


@app.get("/users/{user_id}")
def get_user_endpoint(
    user_id: int,
):
    user = get_user(user_id)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found.",
        )

    return {
        "user_id": user.user_id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "status": user.status,
        "created_at": user.created_at,
    }


@app.post("/auth/login")
def login_endpoint(
    request: UserLogin,
):
    user = authenticate_user(
        username=request.username,
        password=request.password,
    )

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password.",
        )

    return {
        "authenticated": True,
        "user_id": user.user_id,
        "username": user.username,
        "role": user.role,
        "status": user.status,
    }


@app.patch("/users/{user_id}/deactivate")
def deactivate_user_endpoint(
    user_id: int,
    admin_user=Depends(require_admin),
):
    try:
        user = deactivate_user(user_id)

        if user is None:
            raise HTTPException(
                status_code=404,
                detail="User not found.",
            )

        return {
            "user_id": user.user_id,
            "username": user.username,
            "status": user.status,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


# =========================================================
# AUDIT API
# =========================================================

@app.post("/audit-logs")
def create_audit_log_endpoint(
    request: AuditLogCreate,
    authenticated_user=Depends(get_authenticated_user),
):
    try:
        log = create_audit_log(
            user_id=request.user_id,
            action=request.action,
            entity_type=request.entity_type,
            entity_id=request.entity_id,
            details=request.details,
        )

        return {
            "audit_id": log.audit_id,
            "user_id": log.user_id,
            "action": log.action,
            "entity_type": log.entity_type,
            "entity_id": log.entity_id,
            "details": log.details,
            "created_at": log.created_at,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


@app.get("/audit-logs/{audit_id}")
def get_audit_log_endpoint(
    audit_id: int,
):
    log = get_audit_log(audit_id)

    if log is None:
        raise HTTPException(
            status_code=404,
            detail="Audit log not found.",
        )

    return {
        "audit_id": log.audit_id,
        "user_id": log.user_id,
        "action": log.action,
        "entity_type": log.entity_type,
        "entity_id": log.entity_id,
        "details": log.details,
        "created_at": log.created_at,
    }


@app.get("/audit-logs/entity/{entity_type}/{entity_id}")
def get_entity_audit_logs_endpoint(
    entity_type: str,
    entity_id: int,
):
    logs = get_entity_audit_logs(
        entity_type=entity_type,
        entity_id=entity_id,
    )

    return [
        {
            "audit_id": log.audit_id,
            "user_id": log.user_id,
            "action": log.action,
            "entity_type": log.entity_type,
            "entity_id": log.entity_id,
            "details": log.details,
            "created_at": log.created_at,
        }
        for log in logs
    ]


@app.get("/audit-logs/user/{user_id}")
def get_user_audit_logs_endpoint(
    user_id: int,
):
    logs = get_user_audit_logs(user_id)

    return [
        {
            "audit_id": log.audit_id,
            "user_id": log.user_id,
            "action": log.action,
            "entity_type": log.entity_type,
            "entity_id": log.entity_id,
            "details": log.details,
            "created_at": log.created_at,
        }
        for log in logs
    ]