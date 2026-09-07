import pandas as pd
import matplotlib.pyplot as plt

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

print("Calibration dataset")
print("-------------------")
print("Rows:", len(df))
print("Features:", len(features))
print("Target:", target)

print("\nTarget statistics:")
print(df[target].describe())

print("\nCorrelation with CO(GT):")
correlations = df[features + [target]].corr()[target].sort_values(ascending=False)
print(correlations)

# Plot the strongest sensor relationship
strongest_feature = correlations.drop(target).abs().idxmax()

print("\nStrongest relationship:")
print(strongest_feature)

plt.figure(figsize=(8, 5))
plt.scatter(
    df[strongest_feature],
    df[target],
    alpha=0.3
)

plt.xlabel(strongest_feature)
plt.ylabel("CO(GT)")
plt.title(f"{strongest_feature} vs CO(GT)")
plt.tight_layout()

plt.savefig("results/v2_sensor_vs_co.png", dpi=150)

print("\nGraph saved to:")
print("results/v2_sensor_vs_co.png")