import os
import pandas as pd
import joblib

from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

INPUT_FILE = "data/v2/co_calibration_dataset.csv"
MODEL_FILE = "models/v2/co_calibration_model.pkl"

features = [
    "PT08.S1(CO)",
    "PT08.S2(NMHC)",
    "PT08.S3(NOx)",
    "PT08.S4(NO2)",
    "PT08.S5(O3)",
    "T",
    "RH",
    "AH"
]

target = "CO(GT)"

df = pd.read_csv(INPUT_FILE)

X = df[features]
y = df[target]

model = Pipeline([
    ("scaler", StandardScaler()),
    ("regressor", LinearRegression())
])

model.fit(X, y)

os.makedirs("models/v2", exist_ok=True)

joblib.dump(
    {
        "model": model,
        "features": features,
        "target": target
    },
    MODEL_FILE
)

print("Final calibration model trained.")
print("Training samples:", len(df))
print("Features:", len(features))
print("Target:", target)
print("\nModel saved to:")
print(MODEL_FILE)