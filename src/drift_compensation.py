import pandas as pd
import numpy as np

from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(
    "data/processed/sensor_data_with_batch.csv"
)

feature_columns = [
    column
    for column in df.columns
    if column.startswith("feature_")
]


# ============================================================
# SPLIT BY TIME
# ============================================================

train_df = df[df["batch"] <= 7].copy()
test_df = df[df["batch"] >= 8].copy()


print("=" * 60)
print("DRIFT COMPENSATION EXPERIMENT")
print("=" * 60)

print("\nTraining batches: 1-7")
print("Testing batches: 8-10")


# ============================================================
# CALCULATE TRAINING REFERENCE
# ============================================================

reference_mean = train_df[feature_columns].mean()
reference_std = train_df[feature_columns].std()

reference_std = reference_std.replace(0, 1)


# ============================================================
# NORMALIZE TRAINING DATA
# ============================================================

X_train = (
    train_df[feature_columns] - reference_mean
) / reference_std

y_train = train_df["label"]


# ============================================================
# NORMALIZE TEST DATA
# ============================================================

X_test = (
    test_df[feature_columns] - reference_mean
) / reference_std

y_test = test_df["label"]


# ============================================================
# MODEL
# ============================================================

model = LogisticRegression(
    max_iter=2000
)


print("\nTraining compensated model...")

model.fit(
    X_train,
    y_train
)


# ============================================================
# PREDICTION
# ============================================================

predictions = model.predict(
    X_test
)


# ============================================================
# EVALUATION
# ============================================================

accuracy = accuracy_score(
    y_test,
    predictions
)


print("\n" + "=" * 60)
print("COMPENSATED MODEL RESULTS")
print("=" * 60)

print(f"\nAccuracy: {accuracy:.4f}")

print("\nClassification Report:")

print(
    classification_report(
        y_test,
        predictions
    )
)


# ============================================================
# BATCH-BY-BATCH RESULTS
# ============================================================

print("\n" + "=" * 60)
print("BATCH PERFORMANCE")
print("=" * 60)

for batch in sorted(test_df["batch"].unique()):

    batch_mask = test_df["batch"] == batch

    batch_predictions = model.predict(
        X_test.loc[batch_mask]
    )

    batch_accuracy = accuracy_score(
        y_test.loc[batch_mask],
        batch_predictions
    )

    print(
        f"Batch {batch}: "
        f"{batch_accuracy:.4f}"
    )