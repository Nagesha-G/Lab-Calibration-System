import uuid

from fastapi.testclient import TestClient

from src.v5.api.main import app
from src.v5.database.database import SessionLocal
from src.v5.database.models import User

from src.v5.database.models import User, AuditLog


client = TestClient(app)


PASSWORD = "TestPassword123"


def unique_username():
    return f"user_{uuid.uuid4().hex[:8]}"


def create_test_user(role="operator"):
    username = unique_username()

    response = client.post(
        "/users",
        json={
            "username": username,
            "email": f"{username}@example.com",
            "password": PASSWORD,
            "role": role,
        },
    )

    assert response.status_code == 200

    return response.json()


def auth_headers(user):
    return {
        "username": user["username"],
        "password": PASSWORD,
    }


def delete_test_user(user_id):
    db = SessionLocal()

    db.query(AuditLog).filter(
        AuditLog.user_id == user_id
    ).delete()

    user = (
        db.query(User)
        .filter(User.user_id == user_id)
        .first()
    )

    if user:
        db.delete(user)

    db.commit()
    db.close()


def test_create_user():
    data = create_test_user()

    try:
        assert data["user_id"] is not None
        assert data["username"]
        assert data["email"]
        assert data["role"] == "operator"
        assert data["status"] == "active"

    finally:
        delete_test_user(data["user_id"])


def test_get_user():
    data = create_test_user()

    try:
        response = client.get(
            f"/users/{data['user_id']}"
        )

        assert response.status_code == 200

        result = response.json()

        assert result["user_id"] == data["user_id"]
        assert result["username"] == data["username"]

    finally:
        delete_test_user(data["user_id"])


def test_get_missing_user():
    response = client.get(
        "/users/999999"
    )

    assert response.status_code == 404


def test_login():
    data = create_test_user()

    try:
        response = client.post(
            "/auth/login",
            json={
                "username": data["username"],
                "password": PASSWORD,
            },
        )

        assert response.status_code == 200

        result = response.json()

        assert result["authenticated"] is True
        assert result["user_id"] == data["user_id"]

    finally:
        delete_test_user(data["user_id"])


def test_invalid_login():
    data = create_test_user()

    try:
        response = client.post(
            "/auth/login",
            json={
                "username": data["username"],
                "password": "WrongPassword",
            },
        )

        assert response.status_code == 401

    finally:
        delete_test_user(data["user_id"])


def test_deactivate_user():
    admin = create_test_user(role="admin")
    target = create_test_user()

    try:
        response = client.patch(
            f"/users/{target['user_id']}/deactivate",
            headers=auth_headers(admin),
        )

        assert response.status_code == 200

        result = response.json()

        assert result["status"] == "inactive"

        login_response = client.post(
            "/auth/login",
            json={
                "username": target["username"],
                "password": PASSWORD,
            },
        )

        assert login_response.status_code == 401

    finally:
        delete_test_user(admin["user_id"])
        delete_test_user(target["user_id"])


def test_create_audit_log():
    user = create_test_user()

    try:
        response = client.post(
            "/audit-logs",
            headers=auth_headers(user),
            json={
                "user_id": user["user_id"],
                "action": "CREATE",
                "entity_type": "instrument",
                "entity_id": 1,
                "details": "Test audit event",
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert data["audit_id"] is not None
        assert data["user_id"] == user["user_id"]
        assert data["action"] == "CREATE"
        assert data["entity_type"] == "instrument"
        assert data["entity_id"] == 1

    finally:
        delete_test_user(user["user_id"])


def test_get_audit_log():
    user = create_test_user()

    try:
        create_response = client.post(
            "/audit-logs",
            headers=auth_headers(user),
            json={
                "user_id": user["user_id"],
                "action": "UPDATE",
                "entity_type": "instrument",
                "entity_id": 1,
                "details": "Updated instrument",
            },
        )

        assert create_response.status_code == 200

        audit_id = create_response.json()["audit_id"]

        response = client.get(
            f"/audit-logs/{audit_id}"
        )

        assert response.status_code == 200

        data = response.json()

        assert data["audit_id"] == audit_id
        assert data["action"] == "UPDATE"

    finally:
        delete_test_user(user["user_id"])


def test_get_missing_audit_log():
    response = client.get(
        "/audit-logs/999999"
    )

    assert response.status_code == 404


def test_get_entity_audit_logs():
    user = create_test_user()

    try:
        entity_id = 999000 + user["user_id"]

        client.post(
            "/audit-logs",
            headers=auth_headers(user),
            json={
                "user_id": user["user_id"],
                "action": "CREATE",
                "entity_type": "test_entity",
                "entity_id": entity_id,
                "details": "First event",
            },
        )

        client.post(
            "/audit-logs",
            headers=auth_headers(user),
            json={
                "user_id": user["user_id"],
                "action": "UPDATE",
                "entity_type": "test_entity",
                "entity_id": entity_id,
                "details": "Second event",
            },
        )

        response = client.get(
            f"/audit-logs/entity/test_entity/{entity_id}"
        )

        assert response.status_code == 200

        data = response.json()

        assert len(data) == 2

    finally:
        delete_test_user(user["user_id"])


def test_get_user_audit_logs():
    user = create_test_user()

    try:
        client.post(
            "/audit-logs",
            headers=auth_headers(user),
            json={
                "user_id": user["user_id"],
                "action": "CREATE",
                "entity_type": "instrument",
                "entity_id": 1,
            },
        )

        response = client.get(
            f"/audit-logs/user/{user['user_id']}"
        )

        assert response.status_code == 200

        data = response.json()

        assert len(data) >= 1
        assert data[0]["user_id"] == user["user_id"]

    finally:
        delete_test_user(user["user_id"])