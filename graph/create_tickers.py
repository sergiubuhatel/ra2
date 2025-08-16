import csv
import sys

def main():
    if len(sys.argv) != 3:
        print("Usage: python script.py <input_file.csv> <output_file.csv>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    with open(input_file, "r", newline="") as infile, open(output_file, "w", newline="") as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        # Skip header
        next(reader, None)

        # Write only ticker column (first column)
        for row in reader:
            if row and row[0].strip():  # avoid empty rows
                writer.writerow([row[0]])

if __name__ == "__main__":
    main()
