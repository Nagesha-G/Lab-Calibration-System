import os
import zipfile
import urllib.request

url = "https://archive.ics.uci.edu/ml/machine-learning-databases/00360/AirQualityUCI.zip"

output_dir = "data/v2"
zip_path = os.path.join(output_dir, "AirQualityUCI.zip")

os.makedirs(output_dir, exist_ok=True)

print("Downloading V2 dataset...")

urllib.request.urlretrieve(url, zip_path)

print("Download completed.")

print("Extracting dataset...")

with zipfile.ZipFile(zip_path, "r") as zip_ref:
    zip_ref.extractall(output_dir)

print("Extraction completed.")

print("\nFiles downloaded:")

for file in os.listdir(output_dir):
    print("-", file)