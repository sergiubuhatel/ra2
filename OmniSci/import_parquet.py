#
# Usage:
# python import_parquet.py /home/ra2/twitter_tables/tweets_2017.parquet tweets_2017
#
import pandas as pd
from pyarrow import parquet
from pymapd import connect
import argparse
import sys

def main():
    parser = argparse.ArgumentParser(description="Import a Parquet file into OmniSci and create a table.")
    parser.add_argument("parquet_file", help="Path to the Parquet file")
    parser.add_argument("table_name", help="Name of the table to create in OmniSci")
    args = parser.parse_args()

    try:
        # Load the parquet file into a DataFrame
        df = parquet.read_table(args.parquet_file).to_pandas()

        # Connect to OmniSci
        conn = connect(user="admin", password="HyperInteractive", host="localhost", dbname="omnisci")

        # Load the DataFrame and create the table
        conn.load_table(args.table_name, df, create=True)

        print(f"✅ Successfully imported {args.parquet_file} into table '{args.table_name}'.")

    except Exception as e:
        print(f"Failed to import Parquet file: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
