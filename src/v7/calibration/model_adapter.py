"""
V7.2 adapter for the existing V2 calibration model.

The model artifact remains the V2 model. V7 provides the
physics-aware measurement input.
"""

from pathlib import Path

import joblib


DEFAULT_MODEL_PATH = (
    Path("models") / "v2" / "co_calibration_model.joblib"
)

EXPECTED_FEATURES = [
    "PT08.S1(CO)",
    "PT08.S2(NMHC)",
    "PT08.S3(NOx)",
    "PT08.S4(NO2)",
    "PT08.S5(O3)",
    "T",
    "RH",
    "AH",
]


class CalibrationModelAdapter:
    """
    Load and execute the existing calibration model.
    """

    def __init__(
        self,
        model_path: str | Path = DEFAULT_MODEL_PATH,
    ):
        self.model_path = Path(model_path)

        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Calibration model not found: {self.model_path}"
            )

        loaded = joblib.load(self.model_path)

        if isinstance(loaded, dict) and "model" in loaded:
            self.model = loaded["model"]
            self.features = loaded.get(
                "features",
                EXPECTED_FEATURES,
            )
            self.target = loaded.get(
                "target",
                "CO(GT)",
            )
        else:
            self.model = loaded
            self.features = EXPECTED_FEATURES
            self.target = "CO(GT)"

        self._validate_model_interface()

    def _validate_model_interface(self) -> None:
        """Validate the model exposes the expected prediction interface."""

        if not hasattr(self.model, "predict"):
            raise TypeError(
                "Calibration model must expose a predict() method."
            )

        missing = [
            feature
            for feature in EXPECTED_FEATURES
            if feature not in self.features
        ]

        if missing:
            raise ValueError(
                "Calibration model is missing expected features: "
                + ", ".join(missing)
            )

    def predict(
        self,
        measurement: dict[str, float],
    ) -> float:
        """Predict the target variable from sensor measurements."""

        missing = [
            feature
            for feature in self.features
            if feature not in measurement
        ]

        if missing:
            raise ValueError(
                "Measurement is missing model features: "
                + ", ".join(missing)
            )

        ordered_values = [
            measurement[feature]
            for feature in self.features
        ]

        prediction = self.model.predict(
            [ordered_values]
        )[0]

        return float(prediction)

    @property
    def model_version(self) -> str:
        """Return the model artifact version identifier."""

        return "v2.0.0"

    @property
    def target_variable(self) -> str:
        """Return the model target."""

        return self.target