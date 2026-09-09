import uuid

from fastapi.testclient import TestClient

from src.v5.api.main import app
from src.v5.database.database import SessionLocal
from src.v5.database.models import Instrument


client = TestClient(app)

MODEL_FILE = "models/v2/co_calibration_model.joblib"


def create_test_instrument():
    unique_id = uuid.uuid4().hex[:8]

    response = client.post(
        "/instruments",
        json={
            "name": "Calibration API Instrument",
            "manufacturer": "Test Manufacturer",
            "model": "CAL-API-1",
            "serial_number": f"CAL-API-{unique_id}",
            "instrument_type": "gas_analyzer",
        },
    )

    assert response.status_code == 200

    return response.json()["instrument_id"]


def delete_test_instrument(instrument_id):
    db = SessionLocal()

    instrument = (
        db.query(Instrument)
        .filter(
            Instrument.instrument_id == instrument_id
        )
        .first()
    )

    if instrument:
        db.delete(instrument)
        db.commit()

    db.close()


def create_test_model():
    unique_id = uuid.uuid4().hex[:8]

    response = client.post(
        "/models",
        json={
            "model_name": f"Calibration Test Model {unique_id}",
            "model_version": "1.0.0",
            "instrument_type": "gas_analyzer",
            "target_variable": "CO(GT)",
            "framework": "scikit-learn",
            "artifact_path": MODEL_FILE,
            "status": "approved",
        },
    )

    assert response.status_code == 200

    return response.json()["model_id"]


def create_test_configuration(instrument_id):
    response = client.post(
        "/configurations",
        json={
            "instrument_id": instrument_id,
            "configuration_name": "CO Calibration",
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


def create_test_policy(instrument_id):
    response = client.post(
        "/policies",
        json={
            "instrument_id": instrument_id,
            "calibration_interval_days": 30,
            "tolerance": 0.5,
            "reference_required": True,
            "active": True,
        },
    )

    assert response.status_code == 200


def create_test_measurement(instrument_id):
    response = client.post(
        "/measurements",
        json={
            "instrument_id": instrument_id,
            "measurement_data": {
                "PT08.S1(CO)": 1200.5,
                "PT08.S2(NMHC)": 1500.2,
                "PT08.S3(NOx)": 800.1,
                "PT08.S4(NO2)": 1100.7,
                "PT08.S5(O3)": 900.4,
                "T": 25.3,
                "RH": 45.2,
                "AH": 1.1,
            },
        },
    )

    assert response.status_code == 200

    return response.json()["measurement_id"]


def prepare_calibration():
    instrument_id = create_test_instrument()

    create_test_configuration(instrument_id)
    create_test_policy(instrument_id)

    model_id = create_test_model()
    measurement_id = create_test_measurement(
        instrument_id
    )

    return (
        instrument_id,
        model_id,
        measurement_id,
    )


def test_run_calibration():
    (
        instrument_id,
        model_id,
        measurement_id,
    ) = prepare_calibration()

    try:
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

        data = response.json()

        assert data["record_id"] is not None
        assert data["instrument_id"] == instrument_id
        assert data["model_id"] == model_id
        assert data["measurement_id"] == measurement_id
        assert data["reference_value"] == 2.0
        assert data["estimated_value"] >= 0
        assert data["status"] in ["PASS", "FAIL"]

    finally:
        delete_test_instrument(instrument_id)


def test_calibration_invalid_instrument():
    response = client.post(
        "/calibrations",
        json={
            "instrument_id": 999999,
            "measurement_id": 999999,
            "model_id": 999999,
            "reference_value": 2.0,
        },
    )

    assert response.status_code == 400


def test_calibration_invalid_reference():
    (
        instrument_id,
        model_id,
        measurement_id,
    ) = prepare_calibration()

    try:
        response = client.post(
            "/calibrations",
            json={
                "instrument_id": instrument_id,
                "measurement_id": measurement_id,
                "model_id": model_id,
                "reference_value": -1.0,
            },
        )

        assert response.status_code == 400

    finally:
        delete_test_instrument(instrument_id)


def test_get_calibration():
    (
        instrument_id,
        model_id,
        measurement_id,
    ) = prepare_calibration()

    try:
        create_response = client.post(
            "/calibrations",
            json={
                "instrument_id": instrument_id,
                "measurement_id": measurement_id,
                "model_id": model_id,
                "reference_value": 2.0,
            },
        )

        assert create_response.status_code == 200

        record_id = (
            create_response.json()["record_id"]
        )

        response = client.get(
            f"/calibrations/{record_id}"
        )

        assert response.status_code == 200

        data = response.json()

        assert data["record_id"] == record_id
        assert data["instrument_id"] == instrument_id

    finally:
        delete_test_instrument(instrument_id)


def test_get_missing_calibration():
    response = client.get(
        "/calibrations/999999"
    )

    assert response.status_code == 404


def test_get_instrument_calibrations():
    (
        instrument_id,
        model_id,
        measurement_id,
    ) = prepare_calibration()

    try:
        create_response = client.post(
            "/calibrations",
            json={
                "instrument_id": instrument_id,
                "measurement_id": measurement_id,
                "model_id": model_id,
                "reference_value": 2.0,
            },
        )

        assert create_response.status_code == 200

        response = client.get(
            f"/instruments/{instrument_id}/calibrations"
        )

        assert response.status_code == 200

        data = response.json()

        assert len(data) == 1
        assert data[0]["instrument_id"] == instrument_id

    finally:
        delete_test_instrument(instrument_id)