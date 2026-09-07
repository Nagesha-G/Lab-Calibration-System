import pandas as pd
import matplotlib.pyplot as plt

from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

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

# Same chronological split as our latest test
split_index = int(len(df) * 0.75)

X_train = X.iloc[:split_index]
X_test = X.iloc[split_index:]

y_train = y.iloc[:split_index]
y_test = y.iloc[split_index:]

model = Pipeline([
    ("scaler", StandardScaler()),
    ("regressor", LinearRegression())
])

model.fit(X_train, y_train)

y_pred = model.predict(X_test)

# Error
error = y_pred - y_test

print("Prediction Error Analysis")
print("-------------------------")

print(f"MAE  : {mean_absolute_error(y_test, y_pred):.4f}")
print(f"RMSE : {mean_squared_error(y_test, y_pred) ** 0.5:.4f}")
print(f"R²   : {r2_score(y_test, y_pred):.4f}")

print("\nPrediction statistics:")
print(f"Minimum prediction: {y_pred.min():.4f}")
print(f"Maximum prediction: {y_pred.max():.4f}")
print(f"Mean prediction   : {y_pred.mean():.4f}")

print("\nError statistics:")
print(f"Minimum error: {error.min():.4f}")
print(f"Maximum error: {error.max():.4f}")
print(f"Mean error   : {error.mean():.4f}")

# Actual vs predicted graph
plt.figure(figsize=(8, 6))

plt.scatter(
    y_test,
    y_pred,
    alpha=0.3
)

plt.xlabel("Actual CO(GT)")
plt.ylabel("Predicted CO")
plt.title("Actual vs Predicted CO")

plt.tight_layout()

plt.savefig(
    "results/v2/actual_vs_predicted_co.png",
    dpi=150
)

print("\nGraph saved:")
print("results/v2/actual_vs_predicted_co.png")