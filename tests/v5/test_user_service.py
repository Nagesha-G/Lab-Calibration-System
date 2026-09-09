import pytest

from src.v5.database.database import SessionLocal
from src.v5.database.models import User

from src.v5.services.user_service import (
    hash_password,
    verify_password,
    create_user,
    get_user,
    authenticate_user,
    deactivate_user,
)


def delete_test_user(user_id):
    db = SessionLocal()

    user = (
        db.query(User)
        .filter(
            User.user_id == user_id
        )
        .first()
    )

    if user:
        db.delete(user)
        db.commit()

    db.close()


def test_password_hash():
    password = "StrongPassword123"

    password_hash = hash_password(
        password
    )

    assert password_hash != password
    assert verify_password(
        password,
        password_hash,
    )


def test_wrong_password():
    password_hash = hash_password(
        "StrongPassword123"
    )

    assert not verify_password(
        "WrongPassword123",
        password_hash,
    )


def test_short_password_rejected():
    with pytest.raises(
        ValueError,
        match="at least 8 characters",
    ):
        hash_password("short")


def test_create_user():
    user = create_user(
        username="test_operator_001",
        email="operator001@example.com",
        password="StrongPassword123",
        role="operator",
    )

    try:
        assert user.user_id is not None
        assert user.username == "test_operator_001"
        assert user.email == "operator001@example.com"
        assert user.role == "operator"
        assert user.status == "active"
        assert user.password_hash != "StrongPassword123"

    finally:
        delete_test_user(user.user_id)


def test_duplicate_username_rejected():
    user = create_user(
        username="duplicate_user",
        email="duplicate1@example.com",
        password="StrongPassword123",
    )

    try:
        with pytest.raises(
            ValueError,
            match="Username already exists",
        ):
            create_user(
                username="duplicate_user",
                email="duplicate2@example.com",
                password="StrongPassword123",
            )

    finally:
        delete_test_user(user.user_id)


def test_duplicate_email_rejected():
    user = create_user(
        username="email_user_1",
        email="same@example.com",
        password="StrongPassword123",
    )

    try:
        with pytest.raises(
            ValueError,
            match="Email already exists",
        ):
            create_user(
                username="email_user_2",
                email="same@example.com",
                password="StrongPassword123",
            )

    finally:
        delete_test_user(user.user_id)


def test_get_user():
    user = create_user(
        username="get_user_test",
        email="getuser@example.com",
        password="StrongPassword123",
    )

    try:
        result = get_user(
            user.user_id
        )

        assert result is not None
        assert (
            result.user_id
            == user.user_id
        )
        assert (
            result.username
            == "get_user_test"
        )

    finally:
        delete_test_user(user.user_id)


def test_successful_authentication():
    user = create_user(
        username="auth_user",
        email="auth@example.com",
        password="StrongPassword123",
    )

    try:
        authenticated = authenticate_user(
            username="auth_user",
            password="StrongPassword123",
        )

        assert authenticated is not None
        assert (
            authenticated.user_id
            == user.user_id
        )

    finally:
        delete_test_user(user.user_id)


def test_wrong_password_authentication():
    user = create_user(
        username="wrong_password_user",
        email="wrongpassword@example.com",
        password="StrongPassword123",
    )

    try:
        authenticated = authenticate_user(
            username="wrong_password_user",
            password="WrongPassword123",
        )

        assert authenticated is None

    finally:
        delete_test_user(user.user_id)


def test_unknown_user_authentication():
    authenticated = authenticate_user(
        username="does_not_exist",
        password="StrongPassword123",
    )

    assert authenticated is None


def test_deactivated_user_cannot_authenticate():
    user = create_user(
        username="inactive_user",
        email="inactive@example.com",
        password="StrongPassword123",
    )

    try:
        deactivated = deactivate_user(
            user.user_id
        )

        assert deactivated.status == "inactive"

        authenticated = authenticate_user(
            username="inactive_user",
            password="StrongPassword123",
        )

        assert authenticated is None

    finally:
        delete_test_user(user.user_id)


def test_deactivate_missing_user():
    with pytest.raises(
        ValueError,
        match="does not exist",
    ):
        deactivate_user(999999)