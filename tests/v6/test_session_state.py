import pytest

from src.v6.hardware.session_state import (
    SessionState,
    validate_transition,
)


def test_created_to_started():
    validate_transition(
        SessionState.CREATED,
        SessionState.STARTED,
    )


def test_started_to_running():
    validate_transition(
        SessionState.STARTED,
        SessionState.RUNNING,
    )


def test_running_to_started():
    validate_transition(
        SessionState.RUNNING,
        SessionState.STARTED,
    )


def test_any_active_state_can_stop():
    validate_transition(
        SessionState.CREATED,
        SessionState.STOPPED,
    )

    validate_transition(
        SessionState.STARTED,
        SessionState.STOPPED,
    )

    validate_transition(
        SessionState.RUNNING,
        SessionState.STOPPED,
    )


def test_stopped_cannot_restart():
    with pytest.raises(ValueError):
        validate_transition(
            SessionState.STOPPED,
            SessionState.STARTED,
        )


def test_created_cannot_run_directly():
    with pytest.raises(ValueError):
        validate_transition(
            SessionState.CREATED,
            SessionState.RUNNING,
        )