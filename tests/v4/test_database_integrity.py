from uuid import uuid4

import pytest

from src.v3.database import SessionLocal
from src.v3.models import Instrument, CalibrationRecord


def unique_serial(prefix="DB-TEST"):
    return f"{prefix}-{uuid4().hex[:12]}"


def create_test_instrument():
    db = SessionLocal()

    instrument = Instrument(
        name="Database Integrity Test Instrument",
        manufacturer="Test Manufacturer",
        model="TEST-100",
        serial_number=unique_serial(),
        instrument_type="CO Sensor",
        status="active",
    )

    db.add(instrument)
    db.commit()
    db.refresh(instrument)

    instrument_id = instrument.instrument_id

    db.close()

    return instrument_id


def delete_test_instrument(instrument_id):
    db = SessionLocal()

    instrument = (
        db.query(Instrument)
        .filter(Instrument.instrument_id == instrument_id)
        .first()
    )

    if instrument:
        db.delete(instrument)
        db.commit()

    db.close()


def calibration_payload(instrument_id):
    return {
        "instrument_id": instrument_id,
        "sensor_1": 1000.0,
        "sensor_2": 1500.0,
        "sensor_3": 800.0,
        "sensor_4": 1200.0,
        "sensor_5": 900.0,
        "temperature": 20.0,
        "humidity": 50.0,
        "absolute_humidity": 10.0,
        "reference_value": 2.0,
        "tolerance": 1.0,
    }


def test_calibration_error_is_correct(client):
    instrument_id = create_test_instrument()

    try:
        response = client.post(
            "/calibrations",
            json=calibration_payload(instrument_id),
        )

        assert response.status_code == 200

        data = response.json()

        expected_error = (
            data["estimated_value"] - data["reference_value"]
        )

        assert data["error"] == pytest.approx(expected_error)

    finally:
        delete_test_instrument(instrument_id)


def test_calibration_status_matches_tolerance(client):
    instrument_id = create_test_instrument()

    try:
        response = client.post(
            "/calibrations",
            json=calibration_payload(instrument_id),
        )

        assert response.status_code == 200

        data = response.json()

        absolute_error = abs(data["error"])

        if absolute_error <= data["tolerance"]:
            expected_status = "PASS"
        else:
            expected_status = "FAIL"

        assert data["status"] == expected_status

    finally:
        delete_test_instrument(instrument_id)


def test_calibration_model_version(client):
    instrument_id = create_test_instrument()

    try:
        response = client.post(
            "/calibrations",
            json=calibration_payload(instrument_id),
        )

        assert response.status_code == 200

        data = response.json()

        assert data["model_version"] == "v2.0.0"

    finally:
        delete_test_instrument(instrument_id)


def test_calibration_record_belongs_to_correct_instrument(client):
    instrument_id = create_test_instrument()

    try:
        response = client.post(
            "/calibrations",
            json=calibration_payload(instrument_id),
        )

        assert response.status_code == 200

        data = response.json()

        assert data["instrument_id"] == instrument_id

    finally:
        delete_test_instrument(instrument_id)


def test_instruments_do_not_share_calibrations(client):
    instrument_1 = create_test_instrument()
    instrument_2 = create_test_instrument()

    try:
        response = client.post(
            "/calibrations",
            json=calibration_payload(instrument_1),
        )

        assert response.status_code == 200

        response_1 = client.get(
            f"/instruments/{instrument_1}/calibrations"
        )

        response_2 = client.get(
            f"/instruments/{instrument_2}/calibrations"
        )

        assert response_1.status_code == 200
        assert response_2.status_code == 200

        records_1 = response_1.json()
        records_2 = response_2.json()

        assert len(records_1) >= 1

        for record in records_1:
            assert record["instrument_id"] == instrument_1

        for record in records_2:
            assert record["instrument_id"] == instrument_2

    finally:
        delete_test_instrument(instrument_1)
        delete_test_instrument(instrument_2)


def test_instrument_summary_isolated(client):
    instrument_1 = create_test_instrument()
    instrument_2 = create_test_instrument()

    try:
        response = client.post(
            "/calibrations",
            json=calibration_payload(instrument_1),
        )

        assert response.status_code == 200

        summary_1 = client.get(
            f"/instruments/{instrument_1}/calibration-summary"
        )

        summary_2 = client.get(
            f"/instruments/{instrument_2}/calibration-summary"
        )

        assert summary_1.status_code == 200
        assert summary_2.status_code == 200

        data_1 = summary_1.json()
        data_2 = summary_2.json()

        assert data_1["instrument_id"] == instrument_1
        assert data_2["instrument_id"] == instrument_2

        assert data_1["total_calibrations"] >= 1
        assert data_2["total_calibrations"] == 0

    finally:
        delete_test_instrument(instrument_1)
        delete_test_instrument(instrument_2)


def test_latest_calibration_belongs_to_instrument(client):
    instrument_id = create_test_instrument()

    try:
        response = client.post(
            "/calibrations",
            json=calibration_payload(instrument_id),
        )

        assert response.status_code == 200

        latest = client.get(
            f"/instruments/{instrument_id}/calibrations/latest"
        )

        assert latest.status_code == 200

        data = latest.json()

        assert data["instrument_id"] == instrument_id

    finally:
        delete_test_instrument(instrument_id)


def test_statistics_total_matches_records(client):
    instrument_id = create_test_instrument()

    try:
        for _ in range(2):
            response = client.post(
                "/calibrations",
                json=calibration_payload(instrument_id),
            )

            assert response.status_code == 200

        records = client.get(
            f"/instruments/{instrument_id}/calibrations"
        )

        statistics = client.get(
            f"/instruments/{instrument_id}/calibration-statistics"
        )

        assert records.status_code == 200
        assert statistics.status_code == 200

        record_data = records.json()
        statistics_data = statistics.json()

        assert statistics_data["total_calibrations"] == len(record_data)

    finally:
        delete_test_instrument(instrument_id)


def test_statistics_mean_absolute_error_non_negative(client):
    instrument_id = create_test_instrument()

    try:
        response = client.post(
            "/calibrations",
            json=calibration_payload(instrument_id),
        )

        assert response.status_code == 200

        statistics = client.get(
            f"/instruments/{instrument_id}/calibration-statistics"
        )

        assert statistics.status_code == 200

        data = statistics.json()

        assert data["mean_absolute_error"] >= 0

    finally:
        delete_test_instrument(instrument_id)


def test_calibration_persists_after_request(client):
    instrument_id = create_test_instrument()

    try:
        response = client.post(
            "/calibrations",
            json=calibration_payload(instrument_id),
        )

        assert response.status_code == 200

        record_id = response.json()["record_id"]

        direct_record = client.get(
            f"/calibrations/{record_id}"
        )

        assert direct_record.status_code == 200

        data = direct_record.json()

        assert data["record_id"] == record_id
        assert data["instrument_id"] == instrument_id

    finally:
        delete_test_instrument(instrument_id)