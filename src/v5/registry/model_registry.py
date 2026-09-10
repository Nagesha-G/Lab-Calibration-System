import hashlib
from pathlib import Path

from src.v5.database.database import SessionLocal
from src.v5.database.models import Model


def calculate_file_hash(file_path: str) -> str:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Model artifact not found: {file_path}"
        )

    sha256 = hashlib.sha256()

    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(8192), b""):
            sha256.update(chunk)

    return sha256.hexdigest()


def register_model(
    model_name: str,
    model_version: str,
    instrument_type: str,
    target_variable: str,
    framework: str,
    artifact_path: str,
    status: str = "registered",
):
    artifact_hash = calculate_file_hash(artifact_path)

    db = SessionLocal()

    try:
        existing_model = (
            db.query(Model)
            .filter(
                Model.model_name == model_name,
                Model.model_version == model_version,
            )
            .first()
        )

        if existing_model is not None:
            raise ValueError(
                "Model with this name and version already exists."
            )

        model = Model(
            model_name=model_name,
            model_version=model_version,
            instrument_type=instrument_type,
            target_variable=target_variable,
            framework=framework,
            artifact_path=artifact_path,
            artifact_hash=artifact_hash,
            status=status,
        )

        db.add(model)
        db.commit()
        db.refresh(model)

        return model

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


def get_model(model_id: int):
    db = SessionLocal()

    try:
        model = (
            db.query(Model)
            .filter(Model.model_id == model_id)
            .first()
        )

        return model

    finally:
        db.close()


def get_approved_models():
    db = SessionLocal()

    try:
        models = (
            db.query(Model)
            .filter(Model.status == "approved")
            .all()
        )

        return models

    finally:
        db.close()


def approve_model(model_id: int):
    db = SessionLocal()

    try:
        model = (
            db.query(Model)
            .filter(Model.model_id == model_id)
            .first()
        )

        if model is None:
            raise ValueError(
                f"Model {model_id} does not exist."
            )

        if model.status == "approved":
            return model

        model.status = "approved"

        db.commit()
        db.refresh(model)

        return model

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()

