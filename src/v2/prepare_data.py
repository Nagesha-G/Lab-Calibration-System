import os
import pandas as pd

INPUT_FILE = "data/v2/AirQualityUCI.csv"
OUTPUT_FILE = "data/v2/air_quality_clean.csv"

# Load dataset
df = pd.read_csv(
    INPUT_FILE,
    sep=";",
    decimal=","
)

print("Original dataset:")
print("Rows:", len(df))
print("Columns:", len(df.columns))

# Remove completely empty columns
df = df.dropna(axis=1, how="all")

# Columns required for our CO calibration experiment
required_columns = [
    "CO(GT)",
    "PT08.S1(CO)",
    "PT08.S2(NMHC)",
    "PT08.S3(NOx)",
    "PT08.S4(NO2)",
    "PT08.S5(O3)",
    "T",
    "RH",
    "AH"
]

# Count -200 values before cleaning
print("\n-200 values before cleaning:")

for column in required_columns:
    count = (df[column] == -200).sum()
    print(f"{column}: {count}")

# Replace -200 with NaN
df[required_columns] = df[required_columns].replace(-200, pd.NA)

# Remove rows with missing required measurements
df = df.dropna(subset=required_columns)

# Save cleaned data
os.makedirs("data/v2", exist_ok=True)

df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\nCleaned dataset:")
print("Rows:", len(df))
print("Columns:", len(df.columns))

print("\nRemaining missing values:")
print(df[required_columns].isna().sum())

print("\nRemaining -200 values:")

for column in required_columns:
    count = (df[column] == -200).sum()
    print(f"{column}: {count}")

print("\nSaved to:")
print(OUTPUT_FILE)