import pandas as pd
import matplotlib.pyplot as plt


# Load batch performance
df = pd.read_csv(
    "results/batch_performance.csv"
)


# Plot
plt.figure(figsize=(8, 5))

plt.plot(
    df["batch"],
    df["accuracy"],
    marker="o"
)

plt.xlabel("Batch")
plt.ylabel("Accuracy")
plt.title("Model Performance on Future Batches")

plt.ylim(0, 1)

plt.grid(True)

plt.savefig(
    "results/model_performance_over_time.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()


print("Performance plot saved:")
print("results/model_performance_over_time.png")