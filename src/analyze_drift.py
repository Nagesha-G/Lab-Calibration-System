import pandas as pd
import matplotlib.pyplot as plt


DATA_FILE = "data/processed/sensor_data_with_batch.csv"


# --------------------------------------------------
# Load data
# --------------------------------------------------

df = pd.read_csv(DATA_FILE)

print("=" * 60)
print("SENSOR DRIFT ANALYSIS")
print("=" * 60)

print("\nDataset shape:")
print(df.shape)


# --------------------------------------------------
# Calculate average feature values per batch
# --------------------------------------------------

feature_columns = [
    column
    for column in df.columns
    if column.startswith("feature_")
]

batch_means = df.groupby("batch")[feature_columns].mean()


print("\nAverage feature values by batch:")
print(batch_means.head())


# --------------------------------------------------
# Plot selected features across batches
# --------------------------------------------------

features_to_plot = [
    "feature_1",
    "feature_2",
    "feature_3",
    "feature_17",
    "feature_33"
]


for feature in features_to_plot:

    plt.figure()

    plt.plot(
        batch_means.index,
        batch_means[feature],
        marker="o"
    )

    plt.title(f"{feature} Mean Across Batches")

    plt.xlabel("Batch")

    plt.ylabel("Mean Feature Value")

    plt.xticks(batch_means.index)

    plt.grid(True)

    plt.tight_layout()

    filename = f"results/{feature}_batch_drift.png"

    plt.savefig(filename)

    plt.show()


print("\nDrift analysis complete.")

print("\nGraphs saved in results/")