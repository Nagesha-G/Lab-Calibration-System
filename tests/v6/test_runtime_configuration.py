import logging

import pytest

from src.v6.config import Settings
from src.v6.logging_config import (
    configure_logging,
    get_logger,
)


def test_default_settings_are_valid():
    settings = Settings()

    assert settings.app_name == "Lab Calibration System"
    assert settings.version == "6.0.0"
    assert settings.environment == "development"
    assert settings.port == 8000
    assert settings.log_level == "INFO"

    assert settings.validate() is True


def test_invalid_port_rejected():
    settings = Settings(port=70000)

    with pytest.raises(
        ValueError,
        match="port must be between",
    ):
        settings.validate()


def test_invalid_log_level_rejected():
    settings = Settings(
        log_level="INVALID"
    )

    with pytest.raises(
        ValueError,
        match="Unsupported log level",
    ):
        settings.validate()


def test_empty_database_rejected():
    settings = Settings(
        database_url=""
    )

    with pytest.raises(
        ValueError,
        match="database_url",
    ):
        settings.validate()


def test_logging_configuration():
    configure_logging("INFO")

    logger = get_logger(
        "lab_calibration_test"
    )

    assert isinstance(
        logger,
        logging.Logger,
    )


def test_empty_logger_name_rejected():
    with pytest.raises(
        ValueError,
        match="Logger name",
    ):
        get_logger("")