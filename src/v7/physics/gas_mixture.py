"""
Gas-mixture calculations based on partial pressures.
"""


def total_pressure(partial_pressures_pa: dict[str, float]) -> float:
    """Calculate total pressure from component partial pressures."""
    if not partial_pressures_pa:
        raise ValueError("At least one gas component is required.")

    for gas, pressure in partial_pressures_pa.items():
        if pressure < 0:
            raise ValueError(
                f"Partial pressure for {gas} cannot be negative."
            )

    return sum(partial_pressures_pa.values())


def mole_fractions(partial_pressures_pa: dict[str, float]) -> dict[str, float]:
    """Calculate mole fraction of each gas."""
    total = total_pressure(partial_pressures_pa)

    if total <= 0:
        raise ValueError("Total pressure must be greater than zero.")

    return {
        gas: pressure / total
        for gas, pressure in partial_pressures_pa.items()
    }