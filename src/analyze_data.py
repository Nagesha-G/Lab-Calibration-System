import pandas as pd

DATA_FILE = "data/processed/sensor_data.csv"

df = pd.read_csv(DATA_FILE)

print("=" * 60)
print("DATASET ANALYSIS")
print("=" * 60)

# Basic information
print("\nDataset shape:")
print(df.shape)

print("\nNumber of rows:", len(df))
print("Number of columns:", len(df.columns))

# Columns
print("\nFirst 10 columns:")
print(df.columns[:10].tolist())

print("\nLast 10 columns:")
print(df.columns[-10:].tolist())

# Data types
print("\nData types:")
print(df.dtypes.value_counts())

# Missing values
print("\nMissing values:")
print(df.isnull().sum().sum())

# Labels
print("\nLabel distribution:")
print(df["label"].value_counts().sort_index())

# Statistics
print("\nFeature statistics:")
print(df.describe().T.head(20))

# Check duplicate rows
print("\nDuplicate rows:")
print(df.duplicated().sum())

print("\n" + "=" * 60)
print("ANALYSIS COMPLETE")
print("=" * 60)