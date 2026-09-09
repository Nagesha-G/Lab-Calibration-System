import uuid

from fastapi.testclient import TestClient

from src.v5.api.main import app


client = TestClient(app)

MODEL_FILE = "models/v2/co_calibration_model.joblib"


def unique_model_data():
    unique_id = uuid.uuid4().hex[:8]

    return {
        "model_name": f"Test Model {unique_id}",
        "model_version": "1.0.0",
        "instrument_type": "gas_analyzer",
        "target_variable": "CO(GT)",
        "framework": "scikit-learn",
        "artifact_path": MODEL_FILE,
        "status": "registered",
    }


def test_register_model():
    model_data = unique_model_data()
    model_data["status"] = "approved"

    response = client.post(
        "/models",
        json=model_data,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["model_id"] is not None
    assert data["model_name"] == model_data["model_name"]
    assert data["model_version"] == "1.0.0"
    assert data["instrument_type"] == "gas_analyzer"
    assert data["target_variable"] == "CO(GT)"
    assert data["framework"] == "scikit-learn"
    assert data["artifact_hash"] is not None
    assert len(data["artifact_hash"]) == 64
    assert data["status"] == "approved"


def test_register_missing_model_file():
    model_data = unique_model_data()

    model_data["artifact_path"] = (
        "models/v2/does_not_exist.joblib"
    )

    response = client.post(
        "/models",
        json=model_data,
    )

    assert response.status_code == 400


def test_get_model():
    model_data = unique_model_data()

    response = client.post(
        "/models",
        json=model_data,
    )

    assert response.status_code == 200

    model_id = response.json()["model_id"]

    response = client.get(
        f"/models/{model_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["model_id"] == model_id
    assert data["model_name"] == model_data["model_name"]


def test_get_missing_model():
    response = client.get(
        "/models/999999"
    )

    assert response.status_code == 404


def test_get_approved_models():
    model_data = unique_model_data()
    model_data["status"] = "approved"

    response = client.post(
        "/models",
        json=model_data,
    )

    assert response.status_code == 200

    response = client.get(
        "/models/approved"
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)

    assert any(
        model["model_name"]
        == model_data["model_name"]
        for model in data
    )


def test_register_duplicate_model():
    model_data = unique_model_data()

    first_response = client.post(
        "/models",
        json=model_data,
    )

    assert first_response.status_code == 200

    second_response = client.post(
        "/models",
        json=model_data,
    )

    assert second_response.status_code == 400