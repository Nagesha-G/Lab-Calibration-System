import pandas as pd

from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score


# Load data
df = pd.read_csv(
    "data/processed/sensor_data_with_batch.csv"
)

feature_columns = [
    column
    for column in df.columns
    if column.startswith("feature_")
]


# Training data: batches 1-7
train_df = df[df["batch"] <= 7]

X_train = train_df[feature_columns]
y_train = train_df["label"]


# Model
model = Pipeline([
    ("scaler", StandardScaler()),
    (
        "classifier",
        LogisticRegression(
            max_iter=2000
        )
    )
])


print("=" * 60)
print("BATCH-BY-BATCH MODEL PERFORMANCE")
print("=" * 60)

print("\nTraining on batches 1-7...")
model.fit(X_train, y_train)


# Test each future batch separately
results = []

for batch_number in sorted(df[df["batch"] >= 8]["batch"].unique()):

    test_df = df[df["batch"] == batch_number]

    X_test = test_df[feature_columns]
    y_test = test_df["label"]

    predictions = model.predict(X_test)

    accuracy = accuracy_score(
        y_test,
        predictions
    )

    results.append({
        "batch": batch_number,
        "samples": len(test_df),
        "accuracy": accuracy
    })


results_df = pd.DataFrame(results)


print("\nResults:")
print(results_df.to_string(index=False))


# Save
results_df.to_csv(
    "results/batch_performance.csv",
    index=False
)

print("\nSaved:")
print("results/batch_performance.csv")