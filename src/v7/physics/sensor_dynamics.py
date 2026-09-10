"""
First-order sensor dynamics.

This approximates the finite response time of a real sensor.
"""


def first_order_step(
    current_value: float,
    target_value: float,
    time_step_seconds: float,
    time_constant_seconds: float,
) -> float:
    """
    Calculate the next sensor value.

    y_next = y + dt/tau * (target - y)
    """
    if time_step_seconds <= 0:
        raise ValueError("Time step must be greater than zero.")

    if time_constant_seconds <= 0:
        raise ValueError("Time constant must be greater than zero.")

    alpha = time_step_seconds / time_constant_seconds

    # Prevent an excessively large step from creating unstable behavior.
    alpha = min(alpha, 1.0)

    return current_value + alpha * (target_value - current_value)