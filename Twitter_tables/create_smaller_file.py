import pandas as pd
import argparse

def extract_rows(input_file, output_file, num_rows=100):
    """Extract the first `num_rows` rows from `input_file` and save to `output_file`."""
    df = pd.read_csv(input_file, nrows=num_rows)
    df.to_csv(output_file, index=False)
    print(f"Created {output_file} with the first {num_rows} rows.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract first N rows from a CSV file.")
    parser.add_argument("input_file", help="Path to the input CSV file")
    parser.add_argument("output_file", help="Path to save the output CSV file")
    parser.add_argument("--rows", type=int, default=100, help="Number of rows to extract (default: 100)")

    args = parser.parse_args()
    extract_rows(args.input_file, args.output_file, args.rows)