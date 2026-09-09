import uuid

from fastapi.testclient import TestClient

from src.v5.api.main import app
from src.v5.database.database import SessionLocal
from src.v5.database.models import User


client = TestClient(app)


def create_test_user(role="operator"):
    username = f"auth_{uuid.uuid4().hex[:8]}"

    response = client.post(
        "/users",
        json={
            "username": username,
            "email": f"{username}@example.com",
            "password": "TestPassword123",
            "role": role,
        },
    )

    assert response.status_code == 200

    return response.json()


def delete_test_user(user_id):
    db = SessionLocal()

    user = (
        db.query(User)
        .filter(User.user_id == user_id)
        .first()
    )

    if user:
        db.delete(user)
        db.commit()

    db.close()


def test_protected_endpoint_requires_authentication():
    response = client.post(
        "/audit-logs",
        json={
            "action": "TEST",
            "entity_type": "instrument",
            "entity_id": 1,
        },
    )

    assert response.status_code == 401


def test_authenticated_user_can_create_audit_log():
    user = create_test_user()

    try:
        response = client.post(
            "/audit-logs",
            headers={
                "username": user["username"],
                "password": "TestPassword123",
            },
            json={
                "action": "TEST",
                "entity_type": "instrument",
                "entity_id": 1,
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert data["user_id"] is None
        assert data["action"] == "TEST"

    finally:
        delete_test_user(user["user_id"])


def test_invalid_credentials_are_rejected():
    user = create_test_user()

    try:
        response = client.post(
            "/audit-logs",
            headers={
                "username": user["username"],
                "password": "WrongPassword",
            },
            json={
                "action": "TEST",
                "entity_type": "instrument",
                "entity_id": 1,
            },
        )

        assert response.status_code == 401

    finally:
        delete_test_user(user["user_id"])


def test_operator_cannot_deactivate_user():
    operator = create_test_user()
    target = create_test_user()

    try:
        response = client.patch(
            f"/users/{target['user_id']}/deactivate",
            headers={
                "username": operator["username"],
                "password": "TestPassword123",
            },
        )

        assert response.status_code == 403

    finally:
        delete_test_user(operator["user_id"])
        delete_test_user(target["user_id"])


def test_admin_can_deactivate_user():
    admin = create_test_user(role="admin")
    target = create_test_user()

    try:
        response = client.patch(
            f"/users/{target['user_id']}/deactivate",
            headers={
                "username": admin["username"],
                "password": "TestPassword123",
            },
        )

        assert response.status_code == 200
        assert response.json()["status"] == "inactive"

    finally:
        delete_test_user(admin["user_id"])
        delete_test_user(target["user_id"])