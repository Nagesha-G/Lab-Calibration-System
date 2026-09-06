import urllib.request
import zipfile
import os

url = "https://archive.ics.uci.edu/static/public/224/gas+sensor+array+drift+dataset.zip"

output_dir = "data/raw"
zip_path = os.path.join(output_dir, "gas_sensor_dataset.zip")

os.makedirs(output_dir, exist_ok=True)

print("Downloading dataset...")

urllib.request.urlretrieve(url, zip_path)

print("Download complete.")

print("Extracting dataset...")

with zipfile.ZipFile(zip_path, "r") as zip_ref:
    zip_ref.extractall(output_dir)

print("Extraction complete.")

print("\nFiles downloaded:")

for root, dirs, files in os.walk(output_dir):
    for file in files:
        print(os.path.join(root, file))