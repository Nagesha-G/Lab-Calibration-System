from uuid import uuid4

from fastapi.testclient import TestClient

from src.v4.api import app


client = TestClient(app)


def unique_serial():
    return f"INTEGRITY-{uuid4().hex[:12]}"


def create_test_instrument():
    payload = {
        "name": "Integrity Test Instrument",
        "manufacturer": "Test Manufacturer",
        "model": "INTEGRITY-001",
        "serial_number": unique_serial(),
        "instrument_type": "CO Sensor"
    }

    response = client.post(
        "/instruments",
        json=payload
    )

    assert response.status_code == 200

    return response.json()["instrument_id"]


def calibration_payload(instrument_id):
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


def delete_instrument(instrument_id):
    response = client.delete(
        f"/instruments/{instrument_id}"
    )

    assert response.status_code == 200


# ============================================================
# CALIBRATION RECORD INTEGRITY
# ============================================================

def test_calibration_error_is_correct():
    instrument_id = create_test_instrument()

    payload = calibration_payload(instrument_id)

    response = client.post(
        "/calibrations",
        json=payload
    )

    assert response.status_code == 200

    data = response.json()

    calculated_error = (
        data["estimated_value"]
        - data["reference_value"]
    )

    assert abs(data["error"] - calculated_error) < 1e-10

    delete_instrument(instrument_id)


def test_calibration_status_matches_tolerance():
    instrument_id = create_test_instrument()

    payload = calibration_payload(instrument_id)

    response = client.post(
        "/calibrations",
        json=payload
    )

    assert response.status_code == 200

    data = response.json()

    absolute_error = abs(data["error"])

    if absolute_error <= data["tolerance"]:
        expected_status = "PASS"
    else:
        expected_status = "FAIL"

    assert data["status"] == expected_status

    delete_instrument(instrument_id)


def test_calibration_model_version():
    instrument_id = create_test_instrument()

    response = client.post(
        "/calibrations",
        json=calibration_payload(instrument_id)
    )

    assert response.status_code == 200

    data = response.json()

    assert data["model_version"] == "v2.0.0"

    delete_instrument(instrument_id)


def test_calibration_record_belongs_to_correct_instrument():
    instrument_id = create_test_instrument()

    response = client.post(
        "/calibrations",
        json=calibration_payload(instrument_id)
    )

    assert response.status_code == 200

    record_id = response.json()["record_id"]

    record_response = client.get(
        f"/calibrations/{record_id}"
    )

    assert record_response.status_code == 200

    record = record_response.json()

    assert record["instrument_id"] == instrument_id

    delete_instrument(instrument_id)


# ============================================================
# INSTRUMENT ISOLATION
# ============================================================

def test_instruments_do_not_share_calibrations():
    instrument_a = create_test_instrument()
    instrument_b = create_test_instrument()

    response = client.post(
        "/calibrations",
        json=calibration_payload(instrument_a)
    )

    assert response.status_code == 200

    records_a = client.get(
        f"/instruments/{instrument_a}/calibrations"
    )

    records_b = client.get(
        f"/instruments/{instrument_b}/calibrations"
    )

    assert records_a.status_code == 200
    assert records_b.status_code == 200

    data_a = records_a.json()
    data_b = records_b.json()

    assert len(data_a) >= 1

    for record in data_a:
        assert record["instrument_id"] == instrument_a

    assert len(data_b) == 0

    delete_instrument(instrument_a)
    delete_instrument(instrument_b)


def test_instrument_summary_isolated():
    instrument_a = create_test_instrument()
    instrument_b = create_test_instrument()

    response = client.post(
        "/calibrations",
        json=calibration_payload(instrument_a)
    )

    assert response.status_code == 200

    summary_a = client.get(
        f"/instruments/{instrument_a}/calibration-summary"
    )

    summary_b = client.get(
        f"/instruments/{instrument_b}/calibration-summary"
    )

    assert summary_a.status_code == 200
    assert summary_b.status_code == 200

    assert summary_a.json()["total_calibrations"] == 1
    assert summary_b.json()["total_calibrations"] == 0

    delete_instrument(instrument_a)
    delete_instrument(instrument_b)


# ============================================================
# LATEST CALIBRATION
# ============================================================

def test_latest_calibration_belongs_to_instrument():
    instrument_id = create_test_instrument()

    response = client.post(
        "/calibrations",
        json=calibration_payload(instrument_id)
    )

    assert response.status_code == 200

    record_id = response.json()["record_id"]

    latest = client.get(
        f"/instruments/{instrument_id}/calibrations/latest"
    )

    assert latest.status_code == 200

    data = latest.json()

    assert data["record_id"] == record_id
    assert data["instrument_id"] == instrument_id

    delete_instrument(instrument_id)


# ============================================================
# STATISTICS INTEGRITY
# ============================================================

def test_statistics_total_matches_records():
    instrument_id = create_test_instrument()

    for _ in range(3):
        response = client.post(
            "/calibrations",
            json=calibration_payload(instrument_id)
        )

        assert response.status_code == 200

    records_response = client.get(
        f"/instruments/{instrument_id}/calibrations"
    )

    statistics_response = client.get(
        f"/instruments/{instrument_id}/calibration-statistics"
    )

    assert records_response.status_code == 200
    assert statistics_response.status_code == 200

    records = records_response.json()
    statistics = statistics_response.json()

    assert statistics["total_calibrations"] == len(records)

    delete_instrument(instrument_id)


def test_statistics_mean_absolute_error_non_negative():
    instrument_id = create_test_instrument()

    response = client.post(
        "/calibrations",
        json=calibration_payload(instrument_id)
    )

    assert response.status_code == 200

    statistics_response = client.get(
        f"/instruments/{instrument_id}/calibration-statistics"
    )

    assert statistics_response.status_code == 200

    statistics = statistics_response.json()

    assert statistics["mean_absolute_error"] >= 0
    assert statistics["maximum_absolute_error"] >= 0
    assert statistics["minimum_absolute_error"] >= 0

    delete_instrument(instrument_id)


# ============================================================
# CALIBRATION PERSISTENCE
# ============================================================

def test_calibration_persists_after_request():
    instrument_id = create_test_instrument()

    response = client.post(
        "/calibrations",
        json=calibration_payload(instrument_id)
    )

    assert response.status_code == 200

    record_id = response.json()["record_id"]

    second_response = client.get(
        f"/calibrations/{record_id}"
    )

    assert second_response.status_code == 200

    assert (
        second_response.json()["record_id"]
        == record_id
    )

    delete_instrument(instrument_id)