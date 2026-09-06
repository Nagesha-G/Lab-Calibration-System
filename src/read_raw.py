file_path = "data/raw/Dataset/batch1.dat"

with open(file_path, "r") as file:

    for i in range(20):
        line = file.readline()

        if not line:
            break

        print(f"LINE {i + 1}:")
        print(line)