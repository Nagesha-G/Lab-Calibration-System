from src.v3.calibration_service import save_calibration


print("Testing valid calibration...")

record = save_calibration(
    instrument_id=1,
    model_version="v2.0.0",
    estimated_value=3.1546,
    reference_value=3.142,
    tolerance=0.10
)

print("Valid calibration saved.")
print("Record ID:", record.record_id)
print("Error:", record.error)
print("Tolerance:", record.tolerance)
print("Status:", record.status)


print("\nTesting invalid calibration...")

try:
    save_calibration(
        instrument_id=1,
        model_version="v2.0.0",
        estimated_value=3.1546,
        reference_value=0,
        tolerance=0.10
    )
except ValueError as e:
    print("Invalid calibration rejected.")
    print("Reason:", e)