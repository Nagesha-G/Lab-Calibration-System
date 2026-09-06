import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# LOAD RESULTS
# ============================================================

baseline = pd.read_csv(
    "results/batch_performance.csv"
)

corrected = pd.read_csv(
    "results/feature_corrected_performance.csv"
)


# ============================================================
# RENAME COLUMNS
# ============================================================

baseline = baseline.rename(
    columns={"accuracy": "baseline_accuracy"}
)

corrected = corrected.rename(
    columns={"accuracy": "corrected_accuracy"}
)


# ============================================================
# COMBINE
# ============================================================

comparison = pd.merge(
    baseline,
    corrected,
    on="batch"
)


# ============================================================
# CALCULATE IMPROVEMENT
# ============================================================

comparison["improvement"] = (
    comparison["corrected_accuracy"]
    - comparison["baseline_accuracy"]
)


print("=" * 60)
print("BASELINE VS DRIFT CORRECTION")
print("=" * 60)

print(
    comparison.to_string(index=False)
)


# ============================================================
# SAVE
# ============================================================

comparison.to_csv(
    "results/model_comparison.csv",
    index=False
)


# ============================================================
# PLOT
# ============================================================

plt.figure(figsize=(8, 5))

plt.plot(
    comparison["batch"],
    comparison["baseline_accuracy"],
    marker="o",
    label="Baseline"
)

plt.plot(
    comparison["batch"],
    comparison["corrected_accuracy"],
    marker="o",
    label="Drift corrected"
)

plt.xlabel("Batch")
plt.ylabel("Accuracy")
plt.title("Baseline vs Drift-Corrected Model")

plt.ylim(0, 1)

plt.legend()
plt.grid(True)

plt.savefig(
    "results/baseline_vs_corrected.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()


print("\nSaved:")
print("results/model_comparison.csv")
print("results/baseline_vs_corrected.png")