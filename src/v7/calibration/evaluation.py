"""
V7.2 calibration experiment evaluation.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class CalibrationEvaluation:
    """Comparison between prediction and reference."""

    predicted_value: float
    reference_value: float
    error: float
    absolute_error: float
    unit: str

    @property
    def passed(self) -> bool:
        """
        Basic evaluation flag.

        This does NOT replace an instrument-specific calibration policy.
        """
        return self.absolute_error == 0.0

    def to_dict(self) -> dict:
        """Return a serializable evaluation."""
        return {
            "predicted_value": self.predicted_value,
            "reference_value": self.reference_value,
            "error": self.error,
            "absolute_error": self.absolute_error,
            "unit": self.unit,
        }


def evaluate_prediction(
    predicted_value: float,
    reference_value: float,
    unit: str = "mg/m³",
) -> CalibrationEvaluation:
    """Calculate signed and absolute prediction error."""

    error = predicted_value - reference_value

    return CalibrationEvaluation(
        predicted_value=predicted_value,
        reference_value=reference_value,
        error=error,
        absolute_error=abs(error),
        unit=unit,
    )


def mean_absolute_error(
    predicted_values: list[float],
    reference_values: list[float],
) -> float:
    """Calculate MAE."""

    if len(predicted_values) != len(reference_values):
        raise ValueError(
            "Prediction and reference lists must have equal length."
        )

    if not predicted_values:
        raise ValueError(
            "At least one prediction is required."
        )

    errors = [
        abs(predicted - reference)
        for predicted, reference in zip(
            predicted_values,
            reference_values,
        )
    ]

    return sum(errors) / len(errors)


def root_mean_squared_error(
    predicted_values: list[float],
    reference_values: list[float],
) -> float:
    """Calculate RMSE."""

    if len(predicted_values) != len(reference_values):
        raise ValueError(
            "Prediction and reference lists must have equal length."
        )

    if not predicted_values:
        raise ValueError(
            "At least one prediction is required."
        )

    squared_errors = [
        (predicted - reference) ** 2
        for predicted, reference in zip(
            predicted_values,
            reference_values,
        )
    ]

    return (
        sum(squared_errors) / len(squared_errors)
    ) ** 0.5