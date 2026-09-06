import os

DATA_DIR = "data/raw"

print("=" * 60)
print("UCI SENSOR DATASET INSPECTION")
print("=" * 60)

for root, dirs, files in os.walk(DATA_DIR):

    for file in files:

        file_path = os.path.join(root, file)

        print("\n" + "-" * 60)
        print("FILE:", file)
        print("PATH:", file_path)

        # Get file size
        size = os.path.getsize(file_path)

        print("SIZE:", size, "bytes")

print("\n" + "=" * 60)
print("INSPECTION COMPLETE")
print("=" * 60)