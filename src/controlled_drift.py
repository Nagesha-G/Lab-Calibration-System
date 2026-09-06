import pandas as pd
import matplotlib.pyplot as plt

DATA_FILE = "data/processed/sensor_data_with_batch.csv"

df = pd.read_csv(DATA_FILE)

print("=" * 60)
print("CLASS-CONTROLLED SENSOR DRIFT ANALYSIS")
print("=" * 60)

# Features we will investigate
features = [
    "feature_1",
    "feature_2",
    "feature_3",
    "feature_17",
    "feature_33"
]

# --------------------------------------------------
# Check how many samples of each class exist
# in each batch
# --------------------------------------------------

counts = (
    df.groupby(["batch", "label"])
      .size()
      .unstack(fill_value=0)
)

print("\nSamples per class and batch:")
print(counts)


# --------------------------------------------------
# Calculate mean feature value for each
# batch + class combination
# --------------------------------------------------

grouped = (
    df.groupby(["batch", "label"])[features]
      .mean()
      .reset_index()
)

print("\nGrouped data:")
print(grouped.head(20))


# --------------------------------------------------
# Plot each feature separately
# --------------------------------------------------

for feature in features:

    plt.figure()

    for label in sorted(df["label"].unique()):

        subset = grouped[grouped["label"] == label]

        plt.plot(
            subset["batch"],
            subset[feature],
            marker="o",
            label=f"Class {label}"
        )

    plt.title(
        f"{feature}: Mean Response by Batch and Class"
    )

    plt.xlabel("Batch")

    plt.ylabel("Mean feature value")

    plt.xticks(sorted(df["batch"].unique()))

    plt.legend()

    plt.grid(True)

    plt.tight_layout()

    filename = (
        f"results/{feature}_controlled_drift.png"
    )

    plt.savefig(filename)

    plt.show()


print("\nAnalysis complete.")

print("Controlled drift graphs saved in results/")