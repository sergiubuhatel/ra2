#
# Example Usage:
# python generate_tickers.py 2023
# Assumes: ./2023/2023_industries.csv
# Outputs: ./2023/ticker_<industry>.csv
#

import sys
import os
from collections import defaultdict

def generate_ticker_files_by_industry(data_dir):
    input_file = os.path.join(data_dir, f"{os.path.basename(data_dir)}_industries.csv")

    if not os.path.isfile(input_file):
        print(f"❌ Error: Input file '{input_file}' does not exist.")
        return

    industry_map = defaultdict(list)

    try:
        with open(input_file, 'r') as infile:
            next(infile)  # Skip header
            for line in infile:
                parts = line.strip().split(',')
                if len(parts) < 2:
                    continue  # Skip malformed lines
                ticker = parts[0].strip()
                industry = parts[1].strip()
                if ticker and industry:
                    industry_map[industry].append(ticker)

        for industry_code, tickers in industry_map.items():
            output_filename = os.path.join(data_dir, f"ticker_{industry_code}.csv")
            with open(output_filename, 'w') as outfile:
                for ticker in tickers:
                    outfile.write(ticker + '\n')
            print(f"✅ Wrote {len(tickers)} tickers to '{output_filename}'")

    except Exception as e:
        print(f"❌ An error occurred: {e}")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python generate_tickers.py <directory>")
        sys.exit(1)

    directory = sys.argv[1]
    if not os.path.isdir(directory):
        print(f"❌ Error: Directory '{directory}' not found.")
        sys.exit(1)

    generate_ticker_files_by_industry(directory)
