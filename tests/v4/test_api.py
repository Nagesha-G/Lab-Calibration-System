from uuid import uuid4

from fastapi.testclient import TestClient

from src.v4.api import app


client = TestClient(app)


def calibration_payload(instrument_id=1):
    return {
        "instrument_id": instrument_id,
        "sensor_1": 1398.0,
        "sensor_2": 2000.0,
        "sensor_3": 900.0,
        "sensor_4": 1500.0,
        "sensor_5": 1700.0,
        "temperature": 20.0,
        "humidity": 50.0,
        "absolute_humidity": 1.0,
        "reference_value": 2.5,
        "tolerance": 0.5
    }


def unique_serial(prefix):
    return f"{prefix}-{uuid4().hex[:12]}"


def test_root():
    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["version"] == "4.0.0"
    assert data["endpoints"] == 21


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_system_status():
    response = client.get("/system/status")

    assert response.status_code == 200

    data = response.json()

    assert data["api"] == "healthy"
    assert data["database"] == "healthy"
    assert data["ml_model"] == "loaded"
    assert data["model_version"] == "v2.0.0"


def test_instruments_overview():
    response = client.get("/instruments/overview")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_instruments():
    response = client.get("/instruments")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_instrument():
    payload = {
        "name": "API Test Instrument",
        "manufacturer": "Test Manufacturer",
        "model": "TEST-001",
        "serial_number": unique_serial("API-TEST"),
        "instrument_type": "CO Sensor"
    }

    response = client.post(
        "/instruments",
        json=payload
    )

    assert response.status_code == 200

    data = response.json()

    assert "instrument_id" in data
    assert data["name"] == payload["name"]
    assert data["manufacturer"] == payload["manufacturer"]
    assert data["model"] == payload["model"]
    assert data["serial_number"] == payload["serial_number"]
    assert data["instrument_type"] == payload["instrument_type"]
    assert data["status"] == "active"


def test_get_instrument():
    response = client.get("/instruments/1")

    assert response.status_code == 200
    assert response.json()["instrument_id"] == 1


def test_get_missing_instrument():
    response = client.get("/instruments/9999")

    assert response.status_code == 200
    assert response.json()["error"] == "Instrument not found"


def test_duplicate_instrument_serial():
    serial = unique_serial("DUPLICATE")

    payload = {
        "name": "Duplicate Test Instrument",
        "manufacturer": "Test Manufacturer",
        "model": "DUP-001",
        "serial_number": serial,
        "instrument_type": "CO Sensor"
    }

    first_response = client.post(
        "/instruments",
        json=payload
    )

    assert first_response.status_code == 200

    second_response = client.post(
        "/instruments",
        json=payload
    )

    assert second_response.status_code == 200
    assert (
        second_response.json()["error"]
        == "Instrument with this serial number already exists"
    )


def test_calibrations():
    response = client.get("/calibrations")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_calibration():
    response = client.post(
        "/calibrations",
        json=calibration_payload()
    )

    assert response.status_code == 200

    data = response.json()

    assert data["instrument_id"] == 1
    assert "record_id" in data
    assert "estimated_value" in data
    assert "reference_value" in data
    assert "error" in data
    assert "tolerance" in data
    assert "status" in data
    assert data["status"] in ["PASS", "FAIL"]


def test_get_calibration():
    response = client.get("/calibrations/1")

    assert response.status_code == 200
    assert response.json()["record_id"] == 1


def test_get_missing_calibration():
    response = client.get("/calibrations/9999")

    assert response.status_code == 200
    assert response.json()["error"] == "Calibration record not found"


def test_instrument_calibrations():
    response = client.get(
        "/instruments/1/calibrations"
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_latest_calibration():
    response = client.get(
        "/instruments/1/calibrations/latest"
    )

    assert response.status_code == 200


def test_calibration_summary():
    response = client.get(
        "/instruments/1/calibration-summary"
    )

    assert response.status_code == 200


def test_calibration_history():
    response = client.get(
        "/instruments/1/calibrations/history",
        params={"limit": 5}
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_calibration_history_invalid_limit():
    response = client.get(
        "/instruments/1/calibrations/history",
        params={"limit": 0}
    )

    assert response.status_code == 200
    assert response.json()["error"] == "Limit must be greater than 0"


def test_instrument_statistics():
    response = client.get(
        "/instruments/1/calibration-statistics"
    )

    assert response.status_code == 200

    data = response.json()

    assert "instrument_id" in data
    assert "total_calibrations" in data
    assert "mean_error" in data
    assert "mean_absolute_error" in data


def test_all_calibration_statistics():
    response = client.get(
        "/calibration-statistics"
    )

    assert response.status_code == 200

    data = response.json()

    assert "total_calibrations" in data
    assert "mean_error" in data
    assert "mean_absolute_error" in data


def test_calibration_status_pass():
    response = client.get(
        "/calibrations/status/PASS"
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_calibration_status_fail():
    response = client.get(
        "/calibrations/status/FAIL"
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_invalid_calibration_status():
    response = client.get(
        "/calibrations/status/INVALID"
    )

    assert response.status_code == 200
    assert response.json()["error"] == "Status must be PASS or FAIL"


def test_calibration_invalid_instrument():
    response = client.post(
        "/calibrations",
        json=calibration_payload(9999)
    )

    assert response.status_code == 200
    assert response.json()["error"] == "Instrument not found"


def test_calibration_invalid_reference():
    payload = calibration_payload()

    payload["reference_value"] = -1.0

    response = client.post(
        "/calibrations",
        json=payload
    )

    assert response.status_code == 400


def test_calibration_invalid_tolerance():
    payload = calibration_payload()

    payload["tolerance"] = -0.5

    response = client.post(
        "/calibrations",
        json=payload
    )

    assert response.status_code == 400


def test_calibration_inactive_instrument():
    status_response = client.patch(
        "/instruments/1/status",
        params={"status": "inactive"}
    )

    assert status_response.status_code == 200

    response = client.post(
        "/calibrations",
        json=calibration_payload()
    )

    assert response.status_code == 200
    assert response.json()["error"] == "Instrument is inactive"

    restore_response = client.patch(
        "/instruments/1/status",
        params={"status": "active"}
    )

    assert restore_response.status_code == 200


def test_invalid_instrument_status():
    response = client.patch(
        "/instruments/1/status",
        params={"status": "invalid"}
    )

    assert response.status_code == 200
    assert (
        response.json()["error"]
        == "Status must be 'active' or 'inactive'"
    )


def test_calibration_schedule_due():
    response = client.get(
        "/calibration-schedule/due"
    )

    assert response.status_code == 200

    data = response.json()

    assert "days" in data
    assert "due_instruments" in data
    assert isinstance(data["due_instruments"], list)


def test_calibration_schedule_invalid_days():
    response = client.get(
        "/calibration-schedule/due",
        params={"days": 0}
    )

    assert response.status_code == 200
    assert response.json()["error"] == "Days must be greater than 0"


def test_delete_instrument():
    payload = {
        "name": "Delete Test Instrument",
        "manufacturer": "Test Manufacturer",
        "model": "DELETE-001",
        "serial_number": unique_serial("DELETE-TEST"),
        "instrument_type": "Test Sensor"
    }

    create_response = client.post(
        "/instruments",
        json=payload
    )

    assert create_response.status_code == 200

    instrument_id = create_response.json()["instrument_id"]

    delete_response = client.delete(
        f"/instruments/{instrument_id}"
    )

    assert delete_response.status_code == 200
    assert delete_response.json()["instrument_id"] == instrument_id

    get_response = client.get(
        f"/instruments/{instrument_id}"
    )

    assert get_response.status_code == 200
    assert get_response.json()["error"] == "Instrument not found"


def test_delete_missing_instrument():
    response = client.delete(
        "/instruments/9999"
    )

    assert response.status_code == 200
    assert response.json()["error"] == "Instrument not found"


def test_delete_missing_calibration():
    response = client.delete(
        "/calibrations/9999"
    )

    assert response.status_code == 200
    assert response.json()["error"] == "Calibration record not found"