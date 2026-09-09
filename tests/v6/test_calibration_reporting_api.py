from fastapi.testclient import TestClient

from src.v6.api.main import app


client = TestClient(app)


def test_calibration_history_endpoint():
    response = client.get(
        "/hardware/instruments/1/calibrations",
        params={"limit": 20},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["instrument_id"] == 1
    assert data["count"] >= 0
    assert isinstance(data["records"], list)


def test_calibration_summary_endpoint():
    response = client.get(
        "/hardware/instruments/1/calibration-summary"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["instrument_id"] == 1
    assert data["total_calibrations"] >= 0
    assert data["pass_count"] >= 0
    assert data["fail_count"] >= 0

    assert (
        data["pass_count"] + data["fail_count"]
        == data["total_calibrations"]
    )

    assert 0 <= data["pass_rate"] <= 100
    assert data["average_absolute_error"] >= 0


def test_invalid_history_instrument_id():
    response = client.get(
        "/hardware/instruments/0/calibrations"
    )

    assert response.status_code == 400


def test_invalid_summary_instrument_id():
    response = client.get(
        "/hardware/instruments/0/calibration-summary"
    )

    assert response.status_code == 400