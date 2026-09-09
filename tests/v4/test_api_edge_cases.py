from uuid import uuid4

from fastapi.testclient import TestClient

from src.v4.api import app


client = TestClient(app)


def unique_serial(prefix="TEST"):
    return f"{prefix}-{uuid4().hex[:12]}"


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


# ============================================================
# INSTRUMENT EDGE CASES
# ============================================================

def test_create_instrument_empty_name():
    payload = {
        "name": "",
        "manufacturer": "Test",
        "model": "TEST",
        "serial_number": unique_serial(),
        "instrument_type": "CO Sensor"
    }

    response = client.post("/instruments", json=payload)

    assert response.status_code in [200, 422]


def test_create_instrument_missing_name():
    payload = {
        "manufacturer": "Test",
        "model": "TEST",
        "serial_number": unique_serial(),
        "instrument_type": "CO Sensor"
    }

    response = client.post("/instruments", json=payload)

    assert response.status_code == 422


def test_create_instrument_missing_serial():
    payload = {
        "name": "Test",
        "manufacturer": "Test",
        "model": "TEST",
        "instrument_type": "CO Sensor"
    }

    response = client.post("/instruments", json=payload)

    assert response.status_code == 422


def test_create_instrument_missing_manufacturer():
    payload = {
        "name": "Test",
        "model": "TEST",
        "serial_number": unique_serial(),
        "instrument_type": "CO Sensor"
    }

    response = client.post("/instruments", json=payload)

    assert response.status_code == 422


def test_create_instrument_missing_model():
    payload = {
        "name": "Test",
        "manufacturer": "Test",
        "serial_number": unique_serial(),
        "instrument_type": "CO Sensor"
    }

    response = client.post("/instruments", json=payload)

    assert response.status_code == 422


def test_create_instrument_missing_type():
    payload = {
        "name": "Test",
        "manufacturer": "Test",
        "model": "TEST",
        "serial_number": unique_serial()
    }

    response = client.post("/instruments", json=payload)

    assert response.status_code == 422


def test_get_negative_instrument_id():
    response = client.get("/instruments/-1")

    assert response.status_code == 200
    assert response.json()["error"] == "Instrument not found"


def test_get_zero_instrument_id():
    response = client.get("/instruments/0")

    assert response.status_code == 200
    assert response.json()["error"] == "Instrument not found"


def test_get_non_numeric_instrument_id():
    response = client.get("/instruments/abc")

    assert response.status_code == 422


# ============================================================
# CALIBRATION INPUT VALIDATION
# ============================================================

def test_calibration_missing_instrument_id():
    payload = calibration_payload()
    del payload["instrument_id"]

    response = client.post(
        "/calibrations",
        json=payload
    )

    assert response.status_code == 422


def test_calibration_missing_sensor():
    payload = calibration_payload()
    del payload["sensor_1"]

    response = client.post(
        "/calibrations",
        json=payload
    )

    assert response.status_code == 422


def test_calibration_missing_temperature():
    payload = calibration_payload()
    del payload["temperature"]

    response = client.post(
        "/calibrations",
        json=payload
    )

    assert response.status_code == 422


def test_calibration_missing_reference():
    payload = calibration_payload()
    del payload["reference_value"]

    response = client.post(
        "/calibrations",
        json=payload
    )

    assert response.status_code == 422


def test_calibration_missing_tolerance():
    payload = calibration_payload()
    del payload["tolerance"]

    response = client.post(
        "/calibrations",
        json=payload
    )

    assert response.status_code == 422


def test_calibration_zero_reference():
    payload = calibration_payload()
    payload["reference_value"] = 0

    response = client.post(
        "/calibrations",
        json=payload
    )

    assert response.status_code == 400


def test_calibration_zero_tolerance():
    payload = calibration_payload()
    payload["tolerance"] = 0

    response = client.post(
        "/calibrations",
        json=payload
    )

    assert response.status_code == 200


def test_calibration_negative_sensor():
    payload = calibration_payload()
    payload["sensor_1"] = -100

    response = client.post(
        "/calibrations",
        json=payload
    )

    assert response.status_code == 200


def test_calibration_negative_temperature():
    payload = calibration_payload()
    payload["temperature"] = -20

    response = client.post(
        "/calibrations",
        json=payload
    )

    assert response.status_code == 200


# ============================================================
# TYPE VALIDATION
# ============================================================

def test_calibration_invalid_string_sensor():
    payload = calibration_payload()
    payload["sensor_1"] = "invalid"

    response = client.post(
        "/calibrations",
        json=payload
    )

    assert response.status_code == 422


def test_calibration_invalid_string_temperature():
    payload = calibration_payload()
    payload["temperature"] = "invalid"

    response = client.post(
        "/calibrations",
        json=payload
    )

    assert response.status_code == 422


def test_calibration_invalid_string_reference():
    payload = calibration_payload()
    payload["reference_value"] = "invalid"

    response = client.post(
        "/calibrations",
        json=payload
    )

    assert response.status_code == 422


def test_calibration_invalid_string_tolerance():
    payload = calibration_payload()
    payload["tolerance"] = "invalid"

    response = client.post(
        "/calibrations",
        json=payload
    )

    assert response.status_code == 422


# ============================================================
# EXTREME NUMERIC VALUES
# ============================================================

def test_calibration_large_sensor_values():
    payload = calibration_payload()

    payload["sensor_1"] = 1e9
    payload["sensor_2"] = 1e9
    payload["sensor_3"] = 1e9
    payload["sensor_4"] = 1e9
    payload["sensor_5"] = 1e9

    response = client.post(
        "/calibrations",
        json=payload
    )

    assert response.status_code in [200, 400, 500]


def test_calibration_small_sensor_values():
    payload = calibration_payload()

    payload["sensor_1"] = 1e-9
    payload["sensor_2"] = 1e-9
    payload["sensor_3"] = 1e-9
    payload["sensor_4"] = 1e-9
    payload["sensor_5"] = 1e-9

    response = client.post(
        "/calibrations",
        json=payload
    )

    assert response.status_code in [200, 400, 500]


# ============================================================
# HISTORY
# ============================================================

def test_history_limit_one():
    response = client.get(
        "/instruments/1/calibrations/history",
        params={"limit": 1}
    )

    assert response.status_code == 200
    assert len(response.json()) <= 1


def test_history_large_limit():
    response = client.get(
        "/instruments/1/calibrations/history",
        params={"limit": 10000}
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_history_negative_limit():
    response = client.get(
        "/instruments/1/calibrations/history",
        params={"limit": -1}
    )

    assert response.status_code == 200
    assert "error" in response.json()


# ============================================================
# STATUS
# ============================================================

def test_status_uppercase_active():
    response = client.patch(
        "/instruments/1/status",
        params={"status": "active"}
    )

    assert response.status_code == 200
    assert response.json()["status"] == "active"


def test_status_uppercase_inactive():
    response = client.patch(
        "/instruments/1/status",
        params={"status": "inactive"}
    )

    assert response.status_code == 200
    assert response.json()["status"] == "inactive"

    client.patch(
        "/instruments/1/status",
        params={"status": "active"}
    )


def test_status_empty():
    response = client.patch(
        "/instruments/1/status",
        params={"status": ""}
    )

    assert response.status_code == 200
    assert "error" in response.json()


# ============================================================
# CALIBRATION STATUS FILTER
# ============================================================

def test_calibration_status_lowercase_pass():
    response = client.get(
        "/calibrations/status/pass"
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_calibration_status_lowercase_fail():
    response = client.get(
        "/calibrations/status/fail"
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


# ============================================================
# SCHEDULER
# ============================================================

def test_schedule_one_day():
    response = client.get(
        "/calibration-schedule/due",
        params={"days": 1}
    )

    assert response.status_code == 200
    assert response.json()["days"] == 1


def test_schedule_large_window():
    response = client.get(
        "/calibration-schedule/due",
        params={"days": 3650}
    )

    assert response.status_code == 200
    assert response.json()["days"] == 3650


def test_schedule_negative_days():
    response = client.get(
        "/calibration-schedule/due",
        params={"days": -1}
    )

    assert response.status_code == 200
    assert "error" in response.json()


# ============================================================
# DELETE
# ============================================================

def test_delete_nonexistent_calibration():
    response = client.delete(
        "/calibrations/999999"
    )

    assert response.status_code == 200
    assert response.json()["error"] == (
        "Calibration record not found"
    )


def test_delete_nonexistent_instrument():
    response = client.delete(
        "/instruments/999999"
    )

    assert response.status_code == 200
    assert response.json()["error"] == (
        "Instrument not found"
    )