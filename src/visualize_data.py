import pandas as pd
import matplotlib.pyplot as plt

DATA_FILE = "data/processed/sensor_data.csv"

df = pd.read_csv(DATA_FILE)

# --------------------------------------------------
# 1. Label distribution
# --------------------------------------------------

df["label"].value_counts().sort_index().plot(kind="bar")

plt.title("Distribution of Sensor Classes")
plt.xlabel("Class")
plt.ylabel("Number of Samples")
plt.tight_layout()

plt.savefig("results/label_distribution.png")
plt.show()


# --------------------------------------------------
# 2. Feature 1 distribution
# --------------------------------------------------

plt.figure()

plt.hist(df["1"], bins=50)

plt.title("Distribution of Feature 1")
plt.xlabel("Feature 1")
plt.ylabel("Frequency")

plt.tight_layout()

plt.savefig("results/feature_1_distribution.png")
plt.show()


# --------------------------------------------------
# 3. Feature 2 distribution
# --------------------------------------------------

plt.figure()

plt.hist(df["2"], bins=50)

plt.title("Distribution of Feature 2")
plt.xlabel("Feature 2")
plt.ylabel("Frequency")

plt.tight_layout()

plt.savefig("results/feature_2_distribution.png")
plt.show()


print("Visualization complete.")
print("Graphs saved in results/")