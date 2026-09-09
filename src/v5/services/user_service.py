from datetime import datetime

import bcrypt

from src.v5.database.database import SessionLocal
from src.v5.database.models import User


def hash_password(password: str) -> str:
    if not password:
        raise ValueError(
            "Password cannot be empty."
        )

    if len(password) < 8:
        raise ValueError(
            "Password must be at least 8 characters."
        )

    password_bytes = password.encode("utf-8")

    if len(password_bytes) > 72:
        raise ValueError(
            "Password cannot exceed 72 bytes."
        )

    password_hash = bcrypt.hashpw(
        password_bytes,
        bcrypt.gensalt(),
    )

    return password_hash.decode("utf-8")


def verify_password(
    password: str,
    password_hash: str,
) -> bool:
    try:
        return bcrypt.checkpw(
            password.encode("utf-8"),
            password_hash.encode("utf-8"),
        )
    except (ValueError, TypeError):
        return False


def create_user(
    username: str,
    email: str,
    password: str,
    role: str = "operator",
):
    db = SessionLocal()

    try:
        if not username.strip():
            raise ValueError(
                "Username cannot be empty."
            )

        if not email.strip():
            raise ValueError(
                "Email cannot be empty."
            )

        existing_username = (
            db.query(User)
            .filter(
                User.username == username
            )
            .first()
        )

        if existing_username is not None:
            raise ValueError(
                "Username already exists."
            )

        existing_email = (
            db.query(User)
            .filter(
                User.email == email
            )
            .first()
        )

        if existing_email is not None:
            raise ValueError(
                "Email already exists."
            )

        password_hash = hash_password(
            password
        )

        user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            role=role,
            status="active",
            created_at=datetime.now(),
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


def get_user(user_id: int):
    db = SessionLocal()

    try:
        return (
            db.query(User)
            .filter(
                User.user_id == user_id
            )
            .first()
        )

    finally:
        db.close()


def authenticate_user(
    username: str,
    password: str,
):
    db = SessionLocal()

    try:
        user = (
            db.query(User)
            .filter(
                User.username == username
            )
            .first()
        )

        if user is None:
            return None

        if user.status != "active":
            return None

        if not verify_password(
            password,
            user.password_hash,
        ):
            return None

        return user

    finally:
        db.close()


def deactivate_user(user_id: int):
    db = SessionLocal()

    try:
        user = (
            db.query(User)
            .filter(
                User.user_id == user_id
            )
            .first()
        )

        if user is None:
            raise ValueError(
                f"User {user_id} does not exist."
            )

        user.status = "inactive"

        db.commit()
        db.refresh(user)

        return user

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()