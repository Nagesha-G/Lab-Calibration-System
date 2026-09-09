from fastapi.testclient import TestClient

from src.v5.api.main import app
from src.v5.database.database import SessionLocal
from src.v5.database.models import Instrument


client = TestClient(app)


def delete_instrument(instrument_id):
    db = SessionLocal()

    instrument = (
        db.query(Instrument)
        .filter(
            Instrument.instrument_id
            == instrument_id
        )
        .first()
    )

    if instrument:
        db.delete(instrument)
        db.commit()

    db.close()


def test_create_instrument():
    response = client.post(
        "/instruments",
        json={
            "name": "API Gas Analyzer",
            "manufacturer": "Test Manufacturer",
            "model": "GA-500",
            "serial_number": "API-TEST-001",
            "instrument_type": "gas_analyzer",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["instrument_id"] is not None
    assert data["name"] == "API Gas Analyzer"
    assert data["manufacturer"] == "Test Manufacturer"
    assert data["model"] == "GA-500"
    assert data["serial_number"] == "API-TEST-001"
    assert data["instrument_type"] == "gas_analyzer"
    assert data["status"] == "active"

    delete_instrument(
        data["instrument_id"]
    )


def test_duplicate_serial_number():
    first = client.post(
        "/instruments",
        json={
            "name": "First Instrument",
            "manufacturer": "Manufacturer",
            "model": "MODEL-1",
            "serial_number": "API-DUPLICATE-001",
            "instrument_type": "gas_analyzer",
        },
    )

    assert first.status_code == 200

    instrument_id = (
        first.json()["instrument_id"]
    )

    try:
        second = client.post(
            "/instruments",
            json={
                "name": "Second Instrument",
                "manufacturer": "Manufacturer",
                "model": "MODEL-2",
                "serial_number": "API-DUPLICATE-001",
                "instrument_type": "gas_analyzer",
            },
        )

        assert second.status_code == 409
        assert (
            second.json()["detail"]
            == "Serial number already exists."
        )

    finally:
        delete_instrument(instrument_id)


def test_get_instruments():
    response = client.post(
        "/instruments",
        json={
            "name": "List Test Instrument",
            "manufacturer": "Manufacturer",
            "model": "LIST-1",
            "serial_number": "API-LIST-001",
            "instrument_type": "gas_analyzer",
        },
    )

    assert response.status_code == 200

    instrument_id = (
        response.json()["instrument_id"]
    )

    try:
        result = client.get(
            "/instruments"
        )

        assert result.status_code == 200

        data = result.json()

        assert isinstance(data, list)

        ids = {
            item["instrument_id"]
            for item in data
        }

        assert instrument_id in ids

    finally:
        delete_instrument(instrument_id)


def test_get_instrument():
    response = client.post(
        "/instruments",
        json={
            "name": "Get Test Instrument",
            "manufacturer": "Manufacturer",
            "model": "GET-1",
            "serial_number": "API-GET-001",
            "instrument_type": "gas_analyzer",
        },
    )

    assert response.status_code == 200

    instrument_id = (
        response.json()["instrument_id"]
    )

    try:
        result = client.get(
            f"/instruments/{instrument_id}"
        )

        assert result.status_code == 200

        data = result.json()

        assert (
            data["instrument_id"]
            == instrument_id
        )

        assert (
            data["serial_number"]
            == "API-GET-001"
        )

    finally:
        delete_instrument(instrument_id)


def test_get_missing_instrument():
    response = client.get(
        "/instruments/999999"
    )

    assert response.status_code == 404
    assert (
        response.json()["detail"]
        == "Instrument not found."
    )


def test_update_instrument_status():
    response = client.post(
        "/instruments",
        json={
            "name": "Status Test Instrument",
            "manufacturer": "Manufacturer",
            "model": "STATUS-1",
            "serial_number": "API-STATUS-001",
            "instrument_type": "gas_analyzer",
        },
    )

    assert response.status_code == 200

    instrument_id = (
        response.json()["instrument_id"]
    )

    try:
        update = client.patch(
            f"/instruments/{instrument_id}/status",
            json={
                "status": "inactive"
            },
        )

        assert update.status_code == 200

        assert (
            update.json()["status"]
            == "inactive"
        )

        result = client.get(
            f"/instruments/{instrument_id}"
        )

        assert (
            result.json()["status"]
            == "inactive"
        )

    finally:
        delete_instrument(instrument_id)


def test_invalid_instrument_status():
    response = client.post(
        "/instruments",
        json={
            "name": "Invalid Status Instrument",
            "manufacturer": "Manufacturer",
            "model": "INVALID-1",
            "serial_number": "API-INVALID-STATUS-001",
            "instrument_type": "gas_analyzer",
        },
    )

    assert response.status_code == 200

    instrument_id = (
        response.json()["instrument_id"]
    )

    try:
        update = client.patch(
            f"/instruments/{instrument_id}/status",
            json={
                "status": "broken"
            },
        )

        assert update.status_code == 400

    finally:
        delete_instrument(instrument_id)


def test_update_missing_instrument():
    response = client.patch(
        "/instruments/999999/status",
        json={
            "status": "inactive"
        },
    )

    assert response.status_code == 404


def test_empty_instrument_name():
    response = client.post(
        "/instruments",
        json={
            "name": "",
            "manufacturer": "Manufacturer",
            "model": "MODEL",
            "serial_number": "API-EMPTY-001",
            "instrument_type": "gas_analyzer",
        },
    )

    assert response.status_code == 400