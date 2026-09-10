"""
Ideal gas law calculations.

Equation:

    P V = n R T
"""

from .constants import R
from .temperature import to_kelvin


def pressure(
    moles: float,
    temperature_c: float,
    volume_m3: float,
) -> float:
    """
    Calculate pressure in Pa.

    P = nRT / V
    """
    if moles < 0:
        raise ValueError("Moles cannot be negative.")

    if volume_m3 <= 0:
        raise ValueError("Volume must be greater than zero.")

    temperature_k = to_kelvin(temperature_c)

    return (moles * R * temperature_k) / volume_m3


def volume(
    moles: float,
    temperature_c: float,
    pressure_pa: float,
) -> float:
    """
    Calculate volume in m³.

    V = nRT / P
    """
    if moles < 0:
        raise ValueError("Moles cannot be negative.")

    if pressure_pa <= 0:
        raise ValueError("Pressure must be greater than zero.")

    temperature_k = to_kelvin(temperature_c)

    return (moles * R * temperature_k) / pressure_pa


def moles(
    pressure_pa: float,
    temperature_c: float,
    volume_m3: float,
) -> float:
    """
    Calculate amount of substance in mol.

    n = PV / RT
    """
    if pressure_pa <= 0:
        raise ValueError("Pressure must be greater than zero.")

    if volume_m3 <= 0:
        raise ValueError("Volume must be greater than zero.")

    temperature_k = to_kelvin(temperature_c)

    return (pressure_pa * volume_m3) / (R * temperature_k)