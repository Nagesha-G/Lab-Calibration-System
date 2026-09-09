from fastapi.testclient import TestClient

from src.v5.api.main import app
from src.v5.database.database import SessionLocal
from src.v5.database.models import Instrument


client = TestClient(app)


def create_test_instrument():
    response = client.post(
        "/instruments",
        json={
            "name": "Policy API Instrument",
            "manufacturer": "Test Manufacturer",
            "model": "POLICY-API-1",
            "serial_number": "POLICY-API-001",
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


def test_create_policy():
    instrument_id = create_test_instrument()

    try:
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

        data = response.json()

        assert data["policy_id"] is not None
        assert data["instrument_id"] == instrument_id
        assert data["calibration_interval_days"] == 30
        assert data["tolerance"] == 0.5
        assert data["reference_required"] is True
        assert data["active"] is True

    finally:
        delete_test_instrument(instrument_id)


def test_create_policy_invalid_instrument():
    response = client.post(
        "/policies",
        json={
            "instrument_id": 999999,
            "calibration_interval_days": 30,
            "tolerance": 0.5,
            "reference_required": True,
            "active": True,
        },
    )

    assert response.status_code == 400


def test_get_policy():
    instrument_id = create_test_instrument()

    try:
        create_response = client.post(
            "/policies",
            json={
                "instrument_id": instrument_id,
                "calibration_interval_days": 60,
                "tolerance": 0.25,
                "reference_required": True,
                "active": True,
            },
        )

        assert create_response.status_code == 200

        policy_id = create_response.json()["policy_id"]

        response = client.get(
            f"/policies/{policy_id}"
        )

        assert response.status_code == 200

        data = response.json()

        assert data["policy_id"] == policy_id
        assert data["instrument_id"] == instrument_id
        assert data["calibration_interval_days"] == 60

    finally:
        delete_test_instrument(instrument_id)


def test_get_missing_policy():
    response = client.get(
        "/policies/999999"
    )

    assert response.status_code == 404


def test_get_instrument_policies():
    instrument_id = create_test_instrument()

    try:
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

        response = client.get(
            f"/instruments/{instrument_id}/policies"
        )

        assert response.status_code == 200

        data = response.json()

        assert len(data) == 1
        assert data[0]["instrument_id"] == instrument_id

    finally:
        delete_test_instrument(instrument_id)


def test_get_active_policy():
    instrument_id = create_test_instrument()

    try:
        create_response = client.post(
            "/policies",
            json={
                "instrument_id": instrument_id,
                "calibration_interval_days": 30,
                "tolerance": 0.5,
                "reference_required": True,
                "active": True,
            },
        )

        assert create_response.status_code == 200

        response = client.get(
            f"/instruments/{instrument_id}/policies/active"
        )

        assert response.status_code == 200

        data = response.json()

        assert data["instrument_id"] == instrument_id
        assert data["active"] is True

    finally:
        delete_test_instrument(instrument_id)


def test_missing_active_policy():
    instrument_id = create_test_instrument()

    try:
        response = client.get(
            f"/instruments/{instrument_id}/policies/active"
        )

        assert response.status_code == 404

    finally:
        delete_test_instrument(instrument_id)