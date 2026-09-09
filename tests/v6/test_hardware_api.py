from fastapi.testclient import TestClient

from src.v6.api.hardware_api import app


client = TestClient(app)


def test_get_drivers():
    response = client.get("/hardware/drivers")

    assert response.status_code == 200

    data = response.json()

    assert "simulated" in data["drivers"]
    assert "serial" in data["drivers"]
    assert "usb" in data["drivers"]
    assert "tcp" in data["drivers"]


def test_create_simulated_session():
    response = client.post(
        "/hardware/sessions",
        json={
            "driver_type": "simulated",
            "instrument_id": 1,
            "model_id": 1,
            "reference_value": 2.0,
            "driver_config": {
                "instrument_id": 1
            },
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["driver_type"] == "simulated"
    assert data["instrument_id"] == 1
    assert data["model_id"] == 1
    assert data["status"] == "created"


def test_session_start_calibrate_stop():
    create_response = client.post(
        "/hardware/sessions",
        json={
            "driver_type": "simulated",
            "instrument_id": 1,
            "model_id": 1,
            "reference_value": 2.0,
            "driver_config": {
                "instrument_id": 1
            },
        },
    )

    assert create_response.status_code == 200

    session_id = create_response.json()["session_id"]

    start_response = client.post(
        f"/hardware/sessions/{session_id}/start"
    )

    assert start_response.status_code == 200
    assert start_response.json()["ready"] is True

    calibration_response = client.post(
        f"/hardware/sessions/{session_id}/calibrate"
    )

    assert calibration_response.status_code == 200

    calibration = calibration_response.json()

    assert calibration["session_id"] == session_id
    assert calibration["record_id"] > 0
    assert calibration["reference_value"] == 2.0
    assert calibration["status"] in {"PASS", "FAIL"}

    stop_response = client.post(
        f"/hardware/sessions/{session_id}/stop"
    )

    assert stop_response.status_code == 200
    assert stop_response.json()["ready"] is False


def test_missing_session_returns_404():
    response = client.get(
        "/hardware/sessions/not-a-real-session"
    )

    assert response.status_code == 404


def test_invalid_driver_rejected():
    response = client.post(
        "/hardware/sessions",
        json={
            "driver_type": "unknown",
            "instrument_id": 1,
            "model_id": 1,
            "reference_value": 2.0,
        },
    )

    assert response.status_code == 400


def test_run_hardware_session():
    create_response = client.post(
        "/hardware/sessions",
        json={
            "driver_type": "simulated",
            "instrument_id": 1,
            "model_id": 1,
            "reference_value": 2.0,
            "driver_config": {
                "instrument_id": 1
            },
        },
    )

    assert create_response.status_code == 200

    session_id = create_response.json()["session_id"]

    start_response = client.post(
        f"/hardware/sessions/{session_id}/start"
    )

    assert start_response.status_code == 200

    run_response = client.post(
        f"/hardware/sessions/{session_id}/run",
        params={
            "number_of_cycles": 3,
            "interval_seconds": 0,
        },
    )

    assert run_response.status_code == 200

    data = run_response.json()

    assert data["session_id"] == session_id
    assert data["cycles_requested"] == 3
    assert data["cycles_completed"] == 3
    assert len(data["results"]) == 3

    for result in data["results"]:
        assert result["record_id"] > 0
        assert result["reference_value"] == 2.0
        assert result["status"] in {"PASS", "FAIL"}

    client.post(
        f"/hardware/sessions/{session_id}/stop"
    )


def test_run_requires_started_session():
    create_response = client.post(
        "/hardware/sessions",
        json={
            "driver_type": "simulated",
            "instrument_id": 1,
            "model_id": 1,
            "reference_value": 2.0,
            "driver_config": {
                "instrument_id": 1
            },
        },
    )

    assert create_response.status_code == 200

    session_id = create_response.json()["session_id"]

    run_response = client.post(
        f"/hardware/sessions/{session_id}/run",
        params={
            "number_of_cycles": 1,
            "interval_seconds": 0,
        },
    )

    assert run_response.status_code == 400
    assert "not ready" in run_response.json()["detail"]