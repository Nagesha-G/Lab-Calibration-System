"""
V6 Application Logging
"""

import logging
import sys


def configure_logging(
    level: str = "INFO",
):
    normalized_level = level.upper()

    numeric_level = getattr(
        logging,
        normalized_level,
        None,
    )

    if not isinstance(numeric_level, int):
        raise ValueError(
            f"Invalid log level: {level}"
        )

    root_logger = logging.getLogger()

    root_logger.setLevel(numeric_level)

    if not root_logger.handlers:
        handler = logging.StreamHandler(
            sys.stdout
        )

        formatter = logging.Formatter(
            fmt=(
                "%(asctime)s | "
                "%(levelname)s | "
                "%(name)s | "
                "%(message)s"
            )
        )

        handler.setFormatter(formatter)
        root_logger.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    if not name or not name.strip():
        raise ValueError(
            "Logger name cannot be empty."
        )

    return logging.getLogger(name)