import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

df = pd.read_csv(
    "data/processed/sensor_data_with_batch.csv"
)

features = [
    "feature_1",
    "feature_2",
    "feature_3",
    "feature_17",
    "feature_33"
]

results = []

for feature in features:

    for label in sorted(df["label"].unique()):

        subset = (
            df[df["label"] == label]
            .groupby("batch")[feature]
            .mean()
            .reset_index()
        )

        if len(subset) < 3:
            continue

        X = subset[["batch"]]
        y = subset[feature]

        model = LinearRegression()
        model.fit(X, y)

        slope = model.coef_[0]
        r2 = model.score(X, y)

        results.append({
            "feature": feature,
            "label": label,
            "slope_per_batch": slope,
            "r2": r2,
            "batches_available": len(subset)
        })


results_df = pd.DataFrame(results)

print("\n" + "=" * 60)
print("DRIFT TREND ANALYSIS")
print("=" * 60)

print(
    results_df
    .sort_values(
        "r2",
        ascending=False
    )
    .to_string(index=False)
)

results_df.to_csv(
    "results/drift_trends.csv",
    index=False
)

print("\nSaved:")
print("results/drift_trends.csv")