from src.v3.calibration_service import save_calibration


tests = [
    ("Negative reference", 3.0, -1.0, 0.1),
    ("Negative estimate", -2.0, 3.0, 0.1),
    ("Negative tolerance", 3.0, 3.0, -0.1),
]


for name, estimated, reference, tolerance in tests:

    print(f"\nTesting: {name}")

    try:
        save_calibration(
            instrument_id=1,
            model_version="v3-test",
            estimated_value=estimated,
            reference_value=reference,
            tolerance=tolerance
        )

        print("ERROR: Invalid value was accepted.")

    except ValueError as e:

        print("Correctly rejected.")
        print("Reason:", e)