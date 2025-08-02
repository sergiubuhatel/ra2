#
# Example Usage:
# python generate_tickers.py 2017_industries.csv tickers.csv
#

import sys

def extract_tickers(input_file, output_file):
    try:
        with open(input_file, 'r') as infile:
            next(infile)  # Skip header
            tickers = [line.split(',')[0].strip() for line in infile if line.strip()]
        
        with open(output_file, 'w') as outfile:
            for ticker in tickers:
                outfile.write(ticker + '\n')
        print(f"Extracted {len(tickers)} tickers to '{output_file}'")
    
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python generate_tickers.py <input_file.csv> <output_file.txt>")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]
    extract_tickers(input_path, output_path)
