import os
import pandas as pd


DATA_DIR = "data/raw/Dataset"
OUTPUT_FILE = "data/processed/sensor_data_with_batch.csv"


def parse_file(file_path, batch_number):

    records = []

    with open(file_path, "r") as file:

        for line in file:

            line = line.strip()

            if not line:
                continue

            parts = line.split()

            # First value = class label
            label = int(parts[0])

            features = {}

            # Remaining values = feature:value
            for item in parts[1:]:

                feature, value = item.split(":")

                features[f"feature_{feature}"] = float(value)

            # Add label
            features["label"] = label

            # Add batch information
            features["batch"] = batch_number

            records.append(features)

    return records


def main():

    all_records = []

    for filename in sorted(os.listdir(DATA_DIR)):

        if filename.endswith(".dat"):

            file_path = os.path.join(DATA_DIR, filename)

            # Extract batch number
            batch_number = int(
                filename.replace("batch", "").replace(".dat", "")
            )

            print(f"Reading {filename}...")

            records = parse_file(
                file_path,
                batch_number
            )

            all_records.extend(records)

            print(f"  Records: {len(records)}")

    df = pd.DataFrame(all_records)

    # Put batch and label first
    feature_columns = [
        column
        for column in df.columns
        if column.startswith("feature_")
    ]

    df = df[
        ["batch", "label"] + feature_columns
    ]

    os.makedirs("data/processed", exist_ok=True)

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("\n" + "=" * 60)
    print("PARSING COMPLETE")
    print("=" * 60)

    print("Total records:", len(df))
    print("Total columns:", len(df.columns))

    print("\nFirst 5 rows:")
    print(df.head())

    print("\nRecords per batch:")
    print(df["batch"].value_counts().sort_index())

    print("\nLabels:")
    print(df["label"].value_counts().sort_index())

    print("\nMissing values:")
    print(df.isnull().sum().sum())

    print("\nSaved to:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()