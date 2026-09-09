import joblib
import pandas as pd

from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


DATA_PATH = "data/v2/co_calibration_dataset.csv"
MODEL_PATH = "models/v2/co_calibration_model.joblib"


FEATURES = [
    "PT08.S1(CO)",
    "PT08.S2(NMHC)",
    "PT08.S3(NOx)",
    "PT08.S4(NO2)",
    "PT08.S5(O3)",
    "T",
    "RH",
    "AH"
]

TARGET = "CO(GT)"


def main():

    data = pd.read_csv(DATA_PATH)

    X = data[FEATURES]
    y = data[TARGET]

    model = Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            ("regressor", LinearRegression())
        ]
    )

    model.fit(X, y)

    joblib.dump(model, MODEL_PATH)

    print("Final calibration model trained successfully.")
    print(f"Training samples: {len(data)}")
    print(f"Features: {len(FEATURES)}")
    print(f"Target: {TARGET}")
    print(f"Model saved to: {MODEL_PATH}")


if __name__ == "__main__":
    main()