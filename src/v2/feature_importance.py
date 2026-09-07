import pandas as pd

from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

INPUT_FILE = "data/v2/co_calibration_dataset.csv"

df = pd.read_csv(INPUT_FILE)

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

X = df[features]
y = df[target]

# Same chronological split
split_index = int(len(df) * 0.75)

X_train = X.iloc[:split_index]
y_train = y.iloc[:split_index]

model = Pipeline([
    ("scaler", StandardScaler()),
    ("regressor", LinearRegression())
])

model.fit(X_train, y_train)

coefficients = model.named_steps["regressor"].coef_

importance = pd.DataFrame({
    "feature": features,
    "coefficient": coefficients,
    "absolute_coefficient": abs(coefficients)
})

importance = importance.sort_values(
    "absolute_coefficient",
    ascending=False
)

print("Sensor Contribution to CO Calibration")
print("--------------------------------------")
print(importance.to_string(index=False))