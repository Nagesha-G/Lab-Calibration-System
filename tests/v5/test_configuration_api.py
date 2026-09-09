from fastapi.testclient import TestClient

from src.v5.api.main import app
from src.v5.database.database import SessionLocal
from src.v5.database.models import Instrument


client = TestClient(app)


def create_test_instrument():
    response = client.post(
        "/instruments",
        json={
            "name": "Configuration API Instrument",
            "manufacturer": "Test Manufacturer",
            "model": "CONFIG-API-1",
            "serial_number": "CONFIG-API-001",
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
            Instrument.instrument_id
            == instrument_id
        )
        .first()
    )

    if instrument:
        db.delete(instrument)
        db.commit()

    db.close()


def test_create_configuration():
    instrument_id = create_test_instrument()

    try:
        response = client.post(
            "/configurations",
            json={
                "instrument_id": instrument_id,
                "configuration_name": "CO Calibration",
                "input_schema": {
                    "PT08.S1(CO)": "sensor_1",
                    "PT08.S2(NMHC)": "sensor_2",
                    "PT08.S3(NOx)": "sensor_3",
                    "PT08.S4(NO2)": "sensor_4",
                    "PT08.S5(O3)": "sensor_5",
                    "T": "temperature",
                    "RH": "humidity",
                    "AH": "absolute_humidity",
                },
                "target_variable": "CO(GT)",
                "unit": "mg/m3",
                "active": True,
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert data["configuration_id"] is not None
        assert data["instrument_id"] == instrument_id
        assert data["configuration_name"] == "CO Calibration"
        assert data["target_variable"] == "CO(GT)"
        assert data["unit"] == "mg/m3"
        assert data["active"] is True
        assert len(data["input_schema"]) == 8

    finally:
        delete_test_instrument(instrument_id)


def test_create_configuration_invalid_instrument():
    response = client.post(
        "/configurations",
        json={
            "instrument_id": 999999,
            "configuration_name": "CO Calibration",
            "input_schema": {
                "sensor_1": "PT08.S1(CO)"
            },
            "target_variable": "CO(GT)",
            "unit": "mg/m3",
        },
    )

    assert response.status_code == 400


def test_get_configuration():
    instrument_id = create_test_instrument()

    try:
        create_response = client.post(
            "/configurations",
            json={
                "instrument_id": instrument_id,
                "configuration_name": "CO Calibration",
                "input_schema": {
                    "sensor_1": "PT08.S1(CO)"
                },
                "target_variable": "CO(GT)",
                "unit": "mg/m3",
            },
        )

        assert create_response.status_code == 200

        configuration_id = (
            create_response.json()["configuration_id"]
        )

        response = client.get(
            f"/configurations/{configuration_id}"
        )

        assert response.status_code == 200

        data = response.json()

        assert (
            data["configuration_id"]
            == configuration_id
        )

        assert (
            data["configuration_name"]
            == "CO Calibration"
        )

    finally:
        delete_test_instrument(instrument_id)


def test_get_missing_configuration():
    response = client.get(
        "/configurations/999999"
    )

    assert response.status_code == 404


def test_get_instrument_configurations():
    instrument_id = create_test_instrument()

    try:
        first = client.post(
            "/configurations",
            json={
                "instrument_id": instrument_id,
                "configuration_name": "Configuration A",
                "input_schema": {
                    "sensor_1": "PT08.S1(CO)"
                },
                "target_variable": "CO(GT)",
                "unit": "mg/m3",
                "active": False,
            },
        )

        second = client.post(
            "/configurations",
            json={
                "instrument_id": instrument_id,
                "configuration_name": "Configuration B",
                "input_schema": {
                    "sensor_2": "PT08.S2(NMHC)"
                },
                "target_variable": "CO(GT)",
                "unit": "mg/m3",
                "active": True,
            },
        )

        assert first.status_code == 200
        assert second.status_code == 200

        response = client.get(
            f"/instruments/{instrument_id}/configurations"
        )

        assert response.status_code == 200

        data = response.json()

        assert len(data) == 2

    finally:
        delete_test_instrument(instrument_id)


def test_get_active_configuration():
    instrument_id = create_test_instrument()

    try:
        create_response = client.post(
            "/configurations",
            json={
                "instrument_id": instrument_id,
                "configuration_name": "Active CO Configuration",
                "input_schema": {
                    "sensor_1": "PT08.S1(CO)"
                },
                "target_variable": "CO(GT)",
                "unit": "mg/m3",
                "active": True,
            },
        )

        assert create_response.status_code == 200

        configuration_id = (
            create_response.json()["configuration_id"]
        )

        response = client.get(
            f"/instruments/{instrument_id}/configurations/active"
        )

        assert response.status_code == 200

        data = response.json()

        assert (
            data["configuration_id"]
            == configuration_id
        )

        assert data["active"] is True

    finally:
        delete_test_instrument(instrument_id)


def test_missing_active_configuration():
    instrument_id = create_test_instrument()

    try:
        response = client.get(
            f"/instruments/{instrument_id}/configurations/active"
        )

        assert response.status_code == 404

    finally:
        delete_test_instrument(instrument_id)