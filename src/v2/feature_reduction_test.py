import pandas as pd

from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

INPUT_FILE = "data/v2/co_calibration_dataset.csv"

df = pd.read_csv(INPUT_FILE)

target = "CO(GT)"

feature_sets = {
    "All 8 features": [
        "PT08.S1(CO)",
        "PT08.S2(NMHC)",
        "PT08.S3(NOx)",
        "PT08.S4(NO2)",
        "PT08.S5(O3)",
        "T",
        "RH",
        "AH"
    ],

    "Top 5 features": [
        "PT08.S2(NMHC)",
        "PT08.S1(CO)",
        "PT08.S4(NO2)",
        "T",
        "PT08.S3(NOx)"
    ],

    "Top 3 features": [
        "PT08.S2(NMHC)",
        "PT08.S1(CO)",
        "PT08.S4(NO2)"
    ],

    "Top 2 features": [
        "PT08.S2(NMHC)",
        "PT08.S1(CO)"
    ]
}

split_index = int(len(df) * 0.75)

y_train = df[target].iloc[:split_index]
y_test = df[target].iloc[split_index:]

print("Feature Reduction Experiment")
print("-----------------------------")

for name, features in feature_sets.items():

    X_train = df[features].iloc[:split_index]
    X_test = df[features].iloc[split_index:]

    model = Pipeline([
        ("scaler", StandardScaler()),
        ("regressor", LinearRegression())
    ])

    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    mae = mean_absolute_error(y_test, y_pred)
    rmse = mean_squared_error(y_test, y_pred) ** 0.5
    r2 = r2_score(y_test, y_pred)

    print(f"\n{name}")
    print(f"Features: {len(features)}")
    print(f"MAE : {mae:.4f}")
    print(f"RMSE: {rmse:.4f}")
    print(f"R²  : {r2:.4f}")