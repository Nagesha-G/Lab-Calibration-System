import pandas as pd

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

# Divide chronological data into 4 periods
n = len(df)
period_size = n // 4

train_end = period_size * 3

X_train = X.iloc[:train_end]
y_train = y.iloc[:train_end]

X_test = X.iloc[train_end:]
y_test = y.iloc[train_end:]

model = Pipeline([
    ("scaler", StandardScaler()),
    ("regressor", LinearRegression())
])

model.fit(X_train, y_train)

y_pred = model.predict(X_test)

mae = mean_absolute_error(y_test, y_pred)
rmse = mean_squared_error(y_test, y_pred) ** 0.5
r2 = r2_score(y_test, y_pred)

print("Time-Based Calibration Test")
print("----------------------------")

print(f"Training samples: {len(X_train)}")
print(f"Testing samples : {len(X_test)}")

print("\nPerformance:")
print(f"MAE  : {mae:.4f}")
print(f"RMSE : {rmse:.4f}")
print(f"R²   : {r2:.4f}")

print("\nActual CO range:")
print(f"Minimum: {y_test.min():.2f}")
print(f"Maximum: {y_test.max():.2f}")

print("\nPredicted CO range:")
print(f"Minimum: {y_pred.min():.2f}")
print(f"Maximum: {y_pred.max():.2f}")