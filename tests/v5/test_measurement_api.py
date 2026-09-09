import uuid

from fastapi.testclient import TestClient

from src.v5.api.main import app
from src.v5.database.database import SessionLocal
from src.v5.database.models import Instrument


client = TestClient(app)


def create_test_instrument():
    unique_id = uuid.uuid4().hex[:8]

    response = client.post(
        "/instruments",
        json={
            "name": "Measurement API Instrument",
            "manufacturer": "Test Manufacturer",
            "model": "MEASUREMENT-API-1",
            "serial_number": f"MEASUREMENT-{unique_id}",
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


def test_create_measurement():
    instrument_id = create_test_instrument()

    try:
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

        data = response.json()

        assert data["measurement_id"] is not None
        assert data["instrument_id"] == instrument_id
        assert data["measurement_data"]["PT08.S1(CO)"] == 1200.5

    finally:
        delete_test_instrument(instrument_id)


def test_create_measurement_invalid_instrument():
    response = client.post(
        "/measurements",
        json={
            "instrument_id": 999999,
            "measurement_data": {
                "sensor_1": 100
            },
        },
    )

    assert response.status_code == 400


def test_create_empty_measurement():
    instrument_id = create_test_instrument()

    try:
        response = client.post(
            "/measurements",
            json={
                "instrument_id": instrument_id,
                "measurement_data": {},
            },
        )

        assert response.status_code == 400

    finally:
        delete_test_instrument(instrument_id)


def test_get_measurement():
    instrument_id = create_test_instrument()

    try:
        create_response = client.post(
            "/measurements",
            json={
                "instrument_id": instrument_id,
                "measurement_data": {
                    "sensor_1": 100.5,
                    "temperature": 25.0,
                },
            },
        )

        assert create_response.status_code == 200

        measurement_id = (
            create_response.json()["measurement_id"]
        )

        response = client.get(
            f"/measurements/{measurement_id}"
        )

        assert response.status_code == 200

        data = response.json()

        assert (
            data["measurement_id"]
            == measurement_id
        )
        assert data["instrument_id"] == instrument_id
        assert data["measurement_data"]["sensor_1"] == 100.5

    finally:
        delete_test_instrument(instrument_id)


def test_get_missing_measurement():
    response = client.get(
        "/measurements/999999"
    )

    assert response.status_code == 404


def test_get_instrument_measurements():
    instrument_id = create_test_instrument()

    try:
        for value in [100, 200, 300]:
            response = client.post(
                "/measurements",
                json={
                    "instrument_id": instrument_id,
                    "measurement_data": {
                        "sensor_1": value
                    },
                },
            )

            assert response.status_code == 200

        response = client.get(
            f"/instruments/{instrument_id}/measurements"
        )

        assert response.status_code == 200

        data = response.json()

        assert len(data) == 3

        for measurement in data:
            assert (
                measurement["instrument_id"]
                == instrument_id
            )

    finally:
        delete_test_instrument(instrument_id)