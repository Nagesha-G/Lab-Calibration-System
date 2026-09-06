import pandas as pd
import numpy as np

# Load processed data
df = pd.read_csv("data/processed/sensor_data_with_batch.csv")

features = [
    "feature_1",
    "feature_2",
    "feature_3",
    "feature_17",
    "feature_33"
]

# Calculate mean for every feature,
# separately for each batch and gas class
grouped = df.groupby(["batch", "label"])[features].mean()

results = []

for feature in features:

    for label in df["label"].unique():

        try:
            first_value = grouped.loc[(1, label), feature]
            last_value = grouped.loc[(10, label), feature]

            absolute_change = last_value - first_value

            if first_value != 0:
                percent_change = (
                    absolute_change / abs(first_value)
                ) * 100
            else:
                percent_change = np.nan

            results.append({
                "feature": feature,
                "label": label,
                "batch_1_mean": first_value,
                "batch_10_mean": last_value,
                "absolute_change": absolute_change,
                "percent_change": percent_change
            })

        except KeyError:
            pass


results_df = pd.DataFrame(results)

print("\n===== SENSOR DRIFT MEASUREMENT =====\n")
print(results_df.to_string(index=False))

# Save results
results_df.to_csv(
    "results/drift_measurements.csv",
    index=False
)

print("\nSaved:")
print("results/drift_measurements.csv")