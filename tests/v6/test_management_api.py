from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient

from src.v5.database.database import SessionLocal
from src.v5.database.models import Model, User
from src.v6.api.main import app


client = TestClient(app)


# ============================================================
# USER MANAGEMENT
# ============================================================


def test_create_user():
    suffix = uuid4().hex[:8]

    payload = {
        "username": f"v6user_{suffix}",
        "email": f"v6user_{suffix}@example.com",
        "password": "TestPassword123!",
        "role": "operator",
    }

    response = client.post("/users", json=payload)

    assert response.status_code == 200

    data = response.json()

    assert data["username"] == payload["username"]
    assert data["email"] == payload["email"]
    assert data["role"] == "operator"
    assert data["status"] == "active"
    assert "password" not in data
    assert "password_hash" not in data

    user_id = data["user_id"]

    db = SessionLocal()
    try:
        user = (
            db.query(User)
            .filter(User.user_id == user_id)
            .first()
        )

        assert user is not None

        # Password must be stored as a hash, never plaintext.
        assert user.password_hash != payload["password"]
        assert user.password_hash.startswith("$2")
    finally:
        db.close()


def test_duplicate_username_rejected():
    suffix = uuid4().hex[:8]

    payload = {
        "username": f"duplicate_{suffix}",
        "email": f"first_{suffix}@example.com",
        "password": "TestPassword123!",
        "role": "operator",
    }

    first_response = client.post(
        "/users",
        json=payload,
    )

    assert first_response.status_code == 200

    duplicate_payload = {
        "username": payload["username"],
        "email": f"second_{suffix}@example.com",
        "password": "AnotherPassword123!",
        "role": "operator",
    }

    second_response = client.post(
        "/users",
        json=duplicate_payload,
    )

    assert second_response.status_code == 400
    assert "already exists" in second_response.json()["detail"]


def test_duplicate_email_rejected():
    suffix = uuid4().hex[:8]

    payload = {
        "username": f"emailuser1_{suffix}",
        "email": f"same_{suffix}@example.com",
        "password": "TestPassword123!",
        "role": "operator",
    }

    first_response = client.post(
        "/users",
        json=payload,
    )

    assert first_response.status_code == 200

    duplicate_payload = {
        "username": f"emailuser2_{suffix}",
        "email": payload["email"],
        "password": "AnotherPassword123!",
        "role": "operator",
    }

    second_response = client.post(
        "/users",
        json=duplicate_payload,
    )

    assert second_response.status_code == 400
    assert "already exists" in second_response.json()["detail"]


def test_login_success():
    suffix = uuid4().hex[:8]

    payload = {
        "username": f"loginuser_{suffix}",
        "email": f"loginuser_{suffix}@example.com",
        "password": "TestPassword123!",
        "role": "operator",
    }

    create_response = client.post(
        "/users",
        json=payload,
    )

    assert create_response.status_code == 200

    response = client.post(
        "/login",
        json={
            "username": payload["username"],
            "password": payload["password"],
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["authenticated"] is True
    assert data["username"] == payload["username"]
    assert data["email"] == payload["email"]
    assert data["role"] == "operator"
    assert data["status"] == "active"

    assert "password" not in data
    assert "password_hash" not in data


def test_login_wrong_password_rejected():
    suffix = uuid4().hex[:8]

    payload = {
        "username": f"wrongpass_{suffix}",
        "email": f"wrongpass_{suffix}@example.com",
        "password": "CorrectPassword123!",
        "role": "operator",
    }

    create_response = client.post(
        "/users",
        json=payload,
    )

    assert create_response.status_code == 200

    response = client.post(
        "/login",
        json={
            "username": payload["username"],
            "password": "WrongPassword123!",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == (
        "Invalid username or password."
    )


def test_get_user():
    suffix = uuid4().hex[:8]

    payload = {
        "username": f"getuser_{suffix}",
        "email": f"getuser_{suffix}@example.com",
        "password": "TestPassword123!",
        "role": "admin",
    }

    create_response = client.post(
        "/users",
        json=payload,
    )

    assert create_response.status_code == 200

    user_id = create_response.json()["user_id"]

    response = client.get(
        f"/users/{user_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["user_id"] == user_id
    assert data["username"] == payload["username"]
    assert data["email"] == payload["email"]
    assert data["role"] == "admin"
    assert data["status"] == "active"

    assert "password" not in data
    assert "password_hash" not in data


def test_deactivate_user():
    suffix = uuid4().hex[:8]

    payload = {
        "username": f"deactivate_{suffix}",
        "email": f"deactivate_{suffix}@example.com",
        "password": "TestPassword123!",
        "role": "operator",
    }

    create_response = client.post(
        "/users",
        json=payload,
    )

    assert create_response.status_code == 200

    user_id = create_response.json()["user_id"]

    response = client.post(
        f"/users/{user_id}/deactivate"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["user_id"] == user_id
    assert data["status"] == "inactive"


def test_deactivated_user_cannot_login():
    suffix = uuid4().hex[:8]

    payload = {
        "username": f"inactive_{suffix}",
        "email": f"inactive_{suffix}@example.com",
        "password": "TestPassword123!",
        "role": "operator",
    }

    create_response = client.post(
        "/users",
        json=payload,
    )

    assert create_response.status_code == 200

    user_id = create_response.json()["user_id"]

    deactivate_response = client.post(
        f"/users/{user_id}/deactivate"
    )

    assert deactivate_response.status_code == 200

    login_response = client.post(
        "/login",
        json={
            "username": payload["username"],
            "password": payload["password"],
        },
    )

    assert login_response.status_code == 401
    assert login_response.json()["detail"] == (
        "Invalid username or password."
    )


def test_nonexistent_user_returns_404():
    response = client.get("/users/999999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found."


# ============================================================
# MODEL MANAGEMENT
# ============================================================


def test_register_model():
    artifact_path = (
        Path("models/v2/co_calibration_model.joblib")
    )

    assert artifact_path.exists()

    suffix = uuid4().hex[:8]

    payload = {
        "model_name": f"V6 Test Model {suffix}",
        "model_version": "6.0.0-test",
        "instrument_type": "gas_analyzer",
        "target_variable": "CO(GT)",
        "framework": "scikit-learn",
        "artifact_path": str(artifact_path),
    }

    response = client.post(
        "/models/register",
        json=payload,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["model_name"] == payload["model_name"]
    assert data["model_version"] == payload["model_version"]
    assert data["instrument_type"] == "gas_analyzer"
    assert data["target_variable"] == "CO(GT)"
    assert data["framework"] == "scikit-learn"
    assert data["status"] == "registered"

    assert data["artifact_hash"]
    assert len(data["artifact_hash"]) == 64


def test_duplicate_model_rejected():
    artifact_path = (
        Path("models/v2/co_calibration_model.joblib")
    )

    assert artifact_path.exists()

    suffix = uuid4().hex[:8]

    payload = {
        "model_name": f"Duplicate Model {suffix}",
        "model_version": "1.0.0",
        "instrument_type": "gas_analyzer",
        "target_variable": "CO(GT)",
        "framework": "scikit-learn",
        "artifact_path": str(artifact_path),
    }

    first_response = client.post(
        "/models/register",
        json=payload,
    )

    assert first_response.status_code == 200

    second_response = client.post(
        "/models/register",
        json=payload,
    )

    assert second_response.status_code == 400
    assert "already exists" in (
        second_response.json()["detail"]
    )


def test_register_nonexistent_model_artifact_rejected():
    suffix = uuid4().hex[:8]

    payload = {
        "model_name": f"Missing Artifact {suffix}",
        "model_version": "1.0.0",
        "instrument_type": "gas_analyzer",
        "target_variable": "CO(GT)",
        "framework": "scikit-learn",
        "artifact_path": (
            "models/v2/does_not_exist.joblib"
        ),
    }

    response = client.post(
        "/models/register",
        json=payload,
    )

    assert response.status_code == 400
    assert "not found" in response.json()["detail"]


def test_approve_model():
    artifact_path = (
        Path("models/v2/co_calibration_model.joblib")
    )

    assert artifact_path.exists()

    suffix = uuid4().hex[:8]

    payload = {
        "model_name": f"Approval Model {suffix}",
        "model_version": "1.0.0",
        "instrument_type": "gas_analyzer",
        "target_variable": "CO(GT)",
        "framework": "scikit-learn",
        "artifact_path": str(artifact_path),
    }

    register_response = client.post(
        "/models/register",
        json=payload,
    )

    assert register_response.status_code == 200

    model_id = register_response.json()["model_id"]

    assert register_response.json()["status"] == "registered"

    approve_response = client.post(
        f"/models/{model_id}/approve"
    )

    assert approve_response.status_code == 200

    data = approve_response.json()

    assert data["model_id"] == model_id
    assert data["status"] == "approved"


def test_approved_model_appears_in_approved_endpoint():
    artifact_path = (
        Path("models/v2/co_calibration_model.joblib")
    )

    assert artifact_path.exists()

    suffix = uuid4().hex[:8]

    payload = {
        "model_name": f"Approved Endpoint Model {suffix}",
        "model_version": "1.0.0",
        "instrument_type": "gas_analyzer",
        "target_variable": "CO(GT)",
        "framework": "scikit-learn",
        "artifact_path": str(artifact_path),
    }

    register_response = client.post(
        "/models/register",
        json=payload,
    )

    assert register_response.status_code == 200

    model_id = register_response.json()["model_id"]

    approve_response = client.post(
        f"/models/{model_id}/approve"
    )

    assert approve_response.status_code == 200

    response = client.get("/models/approved")

    assert response.status_code == 200

    data = response.json()

    matching_models = [
        model
        for model in data["models"]
        if model["model_id"] == model_id
    ]

    assert len(matching_models) == 1
    assert matching_models[0]["status"] == "approved"


def test_approve_nonexistent_model_returns_404():
    response = client.post(
        "/models/999999999/approve"
    )

    assert response.status_code == 404
    assert "does not exist" in response.json()["detail"]