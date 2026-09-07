import pandas as pd

INPUT_FILE = "data/v2/air_quality_clean.csv"
OUTPUT_FILE = "data/v2/co_calibration_dataset.csv"

df = pd.read_csv(INPUT_FILE)

features = [
    "PT08.S1(CO)",
    "PT08.S2(NMHC)",
    "PT08.S3(NOx)",
    "PT08.S4(NO2)",
    "PT08.S5(O3)",
    "T",
    "RH",
    "AH"
]

target = "CO(GT)"

calibration_df = df[features + [target]].copy()

calibration_df.to_csv(OUTPUT_FILE, index=False)

print("Calibration dataset created.")
print("Rows:", len(calibration_df))
print("Features:", features)
print("Target:", target)
print("\nFirst 5 rows:")
print(calibration_df.head().to_string())