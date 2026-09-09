import uuid

from fastapi.testclient import TestClient

from src.v5.api.main import app
from src.v5.database.database import SessionLocal
from src.v5.database.models import (
    User,
    Instrument,
    InstrumentConfiguration,
    CalibrationPolicy,
    Measurement,
    CalibrationRecord,
    AuditLog,
    Model,
)


client = TestClient(app)


PASSWORD = "TestPassword123"


def cleanup_database():
    db = SessionLocal()

    db.query(AuditLog).delete()
    db.query(CalibrationRecord).delete()
    db.query(Measurement).delete()
    db.query(CalibrationPolicy).delete()
    db.query(InstrumentConfiguration).delete()
    db.query(Model).delete()
    db.query(Instrument).delete()
    db.query(User).delete()

    db.commit()
    db.close()


def test_complete_calibration_workflow():
    cleanup_database()

    # --------------------------------------------------
    # 1. CREATE ADMIN USER
    # --------------------------------------------------

    username = f"e2e_admin_{uuid.uuid4().hex[:8]}"

    response = client.post(
        "/users",
        json={
            "username": username,
            "email": f"{username}@example.com",
            "password": PASSWORD,
            "role": "admin",
        },
    )

    assert response.status_code == 200

    user = response.json()

    assert user["username"] == username
    assert user["role"] == "admin"

    auth_headers = {
        "username": username,
        "password": PASSWORD,
    }

    # --------------------------------------------------
    # 2. CREATE INSTRUMENT
    # --------------------------------------------------

    response = client.post(
        "/instruments",
        json={
            "name": "E2E Gas Analyzer",
            "manufacturer": "Test Manufacturer",
            "model": "GA-E2E",
            "serial_number": f"E2E-{uuid.uuid4().hex[:8]}",
            "instrument_type": "gas_analyzer",
        },
    )

    assert response.status_code == 200

    instrument = response.json()
    instrument_id = instrument["instrument_id"]

    assert instrument["status"] == "active"

    # --------------------------------------------------
    # 3. CREATE CONFIGURATION
    # --------------------------------------------------

    response = client.post(
        "/configurations",
        json={
            "instrument_id": instrument_id,
            "configuration_name": "CO Calibration Configuration",
            "input_schema": {
                "PT08.S1(CO)": "PT08.S1(CO)",
                "PT08.S2(NMHC)": "PT08.S2(NMHC)",
                "PT08.S3(NOx)": "PT08.S3(NOx)",
                "PT08.S4(NO2)": "PT08.S4(NO2)",
                "PT08.S5(O3)": "PT08.S5(O3)",
                "T": "T",
                "RH": "RH",
                "AH": "AH",
            },
            "target_variable": "CO(GT)",
            "unit": "mg/m3",
            "active": True,
        },
    )

    assert response.status_code == 200

    configuration = response.json()

    assert configuration["instrument_id"] == instrument_id
    assert configuration["active"] is True

    # --------------------------------------------------
    # 4. CREATE CALIBRATION POLICY
    # --------------------------------------------------

    response = client.post(
        "/policies",
        json={
            "instrument_id": instrument_id,
            "calibration_interval_days": 30,
            "tolerance": 1.0,
            "reference_required": True,
            "active": True,
        },
    )

    assert response.status_code == 200

    policy = response.json()

    assert policy["instrument_id"] == instrument_id
    assert policy["calibration_interval_days"] == 30
    assert policy["tolerance"] == 1.0

    # --------------------------------------------------
    # 5. REGISTER MODEL
    # --------------------------------------------------

    response = client.post(
        "/models",
        json={
            "model_name": "CO Calibration E2E",
            "model_version": "1.0.0",
            "instrument_type": "gas_analyzer",
            "target_variable": "CO(GT)",
            "framework": "scikit-learn",
            "artifact_path": "models/v2/co_calibration_model.joblib",
            "status": "registered",
        },
    )

    assert response.status_code == 200

    model = response.json()
    model_id = model["model_id"]

    assert model["model_name"] == "CO Calibration E2E"
    assert model["artifact_hash"]

    # --------------------------------------------------
    # 6. APPROVE MODEL DIRECTLY IN DATABASE
    # --------------------------------------------------

    db = SessionLocal()

    db_model = (
        db.query(Model)
        .filter(Model.model_id == model_id)
        .first()
    )

    db_model.status = "approved"

    db.commit()
    db.close()

    # --------------------------------------------------
    # 7. CREATE MEASUREMENT
    # --------------------------------------------------

    response = client.post(
        "/measurements",
        json={
            "instrument_id": instrument_id,
            "measurement_data": {
                "PT08.S1(CO)": 1000.0,
                "PT08.S2(NMHC)": 900.0,
                "PT08.S3(NOx)": 700.0,
                "PT08.S4(NO2)": 1200.0,
                "PT08.S5(O3)": 800.0,
                "T": 20.0,
                "RH": 50.0,
                "AH": 0.8,
            },
        },
    )

    assert response.status_code == 200

    measurement = response.json()
    measurement_id = measurement["measurement_id"]

    assert measurement["instrument_id"] == instrument_id

    # --------------------------------------------------
    # 8. RUN CALIBRATION
    # --------------------------------------------------

    response = client.post(
        "/calibrations",
        json={
            "instrument_id": instrument_id,
            "measurement_id": measurement_id,
            "model_id": model_id,
            "reference_value": 2.0,
        },
    )

    assert response.status_code == 200

    calibration = response.json()

    assert calibration["instrument_id"] == instrument_id
    assert calibration["model_id"] == model_id
    assert calibration["measurement_id"] == measurement_id

    assert calibration["estimated_value"] >= 0
    assert calibration["reference_value"] == 2.0

    assert calibration["status"] in ["PASS", "FAIL"]

    # --------------------------------------------------
    # 9. CREATE AUDIT LOG
    # --------------------------------------------------

    response = client.post(
        "/audit-logs",
        headers=auth_headers,
        json={
            "user_id": user["user_id"],
            "action": "CALIBRATION_EXECUTED",
            "entity_type": "calibration",
            "entity_id": calibration["record_id"],
            "details": "End-to-end calibration test",
        },
    )

    assert response.status_code == 200

    audit = response.json()

    assert audit["action"] == "CALIBRATION_EXECUTED"
    assert audit["entity_type"] == "calibration"

    # --------------------------------------------------
    # 10. VERIFY CALIBRATION HISTORY
    # --------------------------------------------------

    response = client.get(
        f"/instruments/{instrument_id}/calibrations"
    )

    assert response.status_code == 200

    history = response.json()

    assert len(history) == 1
    assert history[0]["record_id"] == calibration["record_id"]

    # --------------------------------------------------
    # 11. VERIFY SYSTEM STATUS
    # --------------------------------------------------

    response = client.get("/system/status")

    assert response.status_code == 200

    status = response.json()

    assert status["database"] == "connected"

    # --------------------------------------------------
    # FINAL ASSERTION
    # --------------------------------------------------

    cleanup_database()