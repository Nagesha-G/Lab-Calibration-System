import pandas as pd

from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(
    "data/processed/sensor_data_with_batch.csv"
)


# ============================================================
# SELECT FEATURES
# ============================================================

feature_columns = [
    column
    for column in df.columns
    if column.startswith("feature_")
]


# ============================================================
# TRAIN / TEST BY BATCH
# ============================================================

train_df = df[df["batch"] <= 7]
test_df = df[df["batch"] >= 8]

X_train = train_df[feature_columns]
y_train = train_df["label"]

X_test = test_df[feature_columns]
y_test = test_df["label"]


print("=" * 60)
print("TIME-BASED BASELINE MODEL")
print("=" * 60)

print("\nTraining batches: 1-7")
print("Testing batches: 8-10")

print(f"\nTraining samples: {len(X_train)}")
print(f"Testing samples:  {len(X_test)}")


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

print("\nTraining model...")

model.fit(
    X_train,
    y_train
)


# ============================================================
# PREDICTION
# ============================================================

y_pred = model.predict(
    X_test
)


# ============================================================
# EVALUATION
# ============================================================

accuracy = accuracy_score(
    y_test,
    y_pred
)


print("\n" + "=" * 60)
print("RESULTS")
print("=" * 60)

print(f"\nAccuracy: {accuracy:.4f}")

print("\nClassification Report:")

print(
    classification_report(
        y_test,
        y_pred
    )
)