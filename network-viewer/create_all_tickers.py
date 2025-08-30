# create_all_tickers.py
#
# Example Usage:
# python create_all_tickers.py \
#   --input ./public/data/2017/2017_Industry.csv \
#   --output ./public/data/2017/All_2017.csv
#

import csv
import argparse

def main():
    parser = argparse.ArgumentParser(description="Extract tickers from CSV")
    parser.add_argument("--input", required=True, help="Path to input CSV file")
    parser.add_argument("--output", required=True, help="Path to output CSV file")
    args = parser.parse_args()

    tickers = []

    # Read input CSV
    with open(args.input, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if row and row[0].strip():  # make sure ticker is not empty
                tickers.append(row[0].strip())

    # Write tickers to output CSV with no header
    with open(args.output, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        for ticker in tickers:
            writer.writerow([ticker])

if __name__ == "__main__":
    main()
