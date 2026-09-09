"""
V6 Runtime Configuration
"""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_name: str = "Lab Calibration System"
    version: str = "6.0.0"

    environment: str = os.getenv(
        "LAB_CALIBRATION_ENV",
        "development",
    )

    host: str = os.getenv(
        "LAB_CALIBRATION_HOST",
        "127.0.0.1",
    )

    port: int = int(
        os.getenv(
            "LAB_CALIBRATION_PORT",
            "8000",
        )
    )

    log_level: str = os.getenv(
        "LAB_CALIBRATION_LOG_LEVEL",
        "INFO",
    )

    database_url: str = os.getenv(
        "LAB_CALIBRATION_DATABASE_URL",
        "sqlite:///database/v5_calibration.db",
    )

    model_path: str = os.getenv(
        "LAB_CALIBRATION_MODEL_PATH",
        "models/v2/co_calibration_model.joblib",
    )

    def validate(self):
        if not self.app_name.strip():
            raise ValueError("app_name cannot be empty.")

        if not self.version.strip():
            raise ValueError("version cannot be empty.")

        if not self.environment.strip():
            raise ValueError("environment cannot be empty.")

        if not self.host.strip():
            raise ValueError("host cannot be empty.")

        if self.port < 1 or self.port > 65535:
            raise ValueError(
                "port must be between 1 and 65535."
            )

        allowed_log_levels = {
            "DEBUG",
            "INFO",
            "WARNING",
            "ERROR",
            "CRITICAL",
        }

        if self.log_level.upper() not in allowed_log_levels:
            raise ValueError(
                f"Unsupported log level: {self.log_level}"
            )

        if not self.database_url.strip():
            raise ValueError(
                "database_url cannot be empty."
            )

        if not self.model_path.strip():
            raise ValueError(
                "model_path cannot be empty."
            )

        return True


settings = Settings()
settings.validate()