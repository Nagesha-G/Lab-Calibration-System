from enum import Enum


class SessionState(str, Enum):
    CREATED = "CREATED"
    STARTED = "STARTED"
    RUNNING = "RUNNING"
    STOPPED = "STOPPED"


VALID_TRANSITIONS = {
    SessionState.CREATED: {
        SessionState.STARTED,
        SessionState.STOPPED,
    },
    SessionState.STARTED: {
        SessionState.RUNNING,
        SessionState.STOPPED,
    },
    SessionState.RUNNING: {
        SessionState.STARTED,
        SessionState.STOPPED,
    },
    SessionState.STOPPED: set(),
}


def validate_transition(
    current_state: SessionState,
    next_state: SessionState,
):
    allowed_states = VALID_TRANSITIONS.get(
        current_state,
        set(),
    )

    if next_state not in allowed_states:
        raise ValueError(
            f"Invalid session transition: "
            f"{current_state.value} -> {next_state.value}"
        )