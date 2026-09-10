"""
Sensor drift models.
"""


def linear_drift(
    initial_bias: float,
    drift_rate_per_day: float,
    elapsed_days: float,
) -> float:
    """
    Calculate sensor bias after elapsed time.

    b(t) = b0 + k*t
    """
    if elapsed_days < 0:
        raise ValueError("Elapsed time cannot be negative.")

    return initial_bias + drift_rate_per_day * elapsed_days


def apply_drift(
    measurement: float,
    initial_bias: float,
    drift_rate_per_day: float,
    elapsed_days: float,
) -> float:
    """Apply linear drift to a measurement."""
    return measurement + linear_drift(
        initial_bias=initial_bias,
        drift_rate_per_day=drift_rate_per_day,
        elapsed_days=elapsed_days,
    )