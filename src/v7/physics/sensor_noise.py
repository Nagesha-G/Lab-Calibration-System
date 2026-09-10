"""
Measurement noise models.
"""

import random


def gaussian_noise(
    standard_deviation: float,
    seed: int | None = None,
) -> float:
    """
    Generate zero-mean Gaussian measurement noise.
    """
    if standard_deviation < 0:
        raise ValueError("Standard deviation cannot be negative.")

    generator = random.Random(seed)

    return generator.gauss(0.0, standard_deviation)


def add_gaussian_noise(
    value: float,
    standard_deviation: float,
    seed: int | None = None,
) -> float:
    """Add Gaussian noise to a measurement."""
    return value + gaussian_noise(
        standard_deviation=standard_deviation,
        seed=seed,
    )