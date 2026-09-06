import pandas as pd
import numpy as np

from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline


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
# SPLIT DATA
# ============================================================

train_df = df[df["batch"] <= 7].copy()
test_df = df[df["batch"] >= 8].copy()

print("=" * 60)
print("FEATURE-WISE DRIFT CORRECTION")
print("=" * 60)

print("\nTraining batches: 1-7")
print("Testing batches: 8-10")


# ============================================================
# ESTIMATE FEATURE DRIFT
# ============================================================

# Average each feature within each training batch
batch_means = train_df.groupby("batch")[feature_columns].mean()

corrected_train = train_df[feature_columns].copy()
corrected_test = test_df[feature_columns].copy()


for feature in feature_columns:

    # Training batch values
    y = batch_means[feature].values
    X = batch_means.index.values.reshape(-1, 1)

    # Fit linear drift model
    drift_model = LinearRegression()
    drift_model.fit(X, y)

    # Reference point = first training batch
    reference_batch = 1

    reference_value = drift_model.predict(
        [[reference_batch]]
    )[0]

    # Correct training data
    train_drift = drift_model.predict(
        train_df[["batch"]]
    )

    corrected_train[feature] = (
        train_df[feature].values
        - train_drift
        + reference_value
    )

    # Correct test data
    test_drift = drift_model.predict(
        test_df[["batch"]]
    )

    corrected_test[feature] = (
        test_df[feature].values
        - test_drift
        + reference_value
    )


# ============================================================
# TARGET
# ============================================================

y_train = train_df["label"]
y_test = test_df["label"]


# ============================================================
# MODEL
# ============================================================

model = Pipeline([
    ("scaler", StandardScaler()),
    (
        "classifier",
        LogisticRegression(
            max_iter=2000
        )
    )
])


# ============================================================
# TRAIN
# ============================================================

print("\nTraining corrected model...")

model.fit(
    corrected_train,
    y_train
)


# ============================================================
# TEST
# ============================================================

predictions = model.predict(
    corrected_test
)


accuracy = accuracy_score(
    y_test,
    predictions
)


print("\n" + "=" * 60)
print("CORRECTED MODEL RESULTS")
print("=" * 60)

print(f"\nOverall Accuracy: {accuracy:.4f}")

print("\nClassification Report:")

print(
    classification_report(
        y_test,
        predictions
    )
)


# ============================================================
# BATCH RESULTS
# ============================================================

print("\n" + "=" * 60)
print("BATCH PERFORMANCE")
print("=" * 60)

results = []

for batch in sorted(test_df["batch"].unique()):

    mask = test_df["batch"] == batch

    batch_predictions = model.predict(
        corrected_test.loc[mask]
    )

    batch_accuracy = accuracy_score(
        y_test.loc[mask],
        batch_predictions
    )

    print(
        f"Batch {batch}: "
        f"{batch_accuracy:.4f}"
    )

    results.append({
        "batch": batch,
        "accuracy": batch_accuracy,
        "samples": mask.sum()
    })


# ============================================================
# SAVE RESULTS
# ============================================================

results_df = pd.DataFrame(results)

results_df.to_csv(
    "results/feature_corrected_performance.csv",
    index=False
)

print("\nSaved:")
print(
    "results/feature_corrected_performance.csv"
)