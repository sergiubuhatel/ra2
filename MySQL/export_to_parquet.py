#
# Example: 
# python export_to_parquet.py tweets_2017 tweets_2018 tweets_2019 tweets_2020 tweets_2021 tweets_2022 tweets_2023
#

import pandas as pd
import sqlalchemy
import argparse
import sys

# Set up command-line argument parsing
parser = argparse.ArgumentParser(description="Export selected MySQL tables to Parquet files.")
parser.add_argument("tables", nargs="+", help="List of MySQL tables to export")
args = parser.parse_args()

# Connect to MySQL
engine = sqlalchemy.create_engine("mysql+pymysql://root:root@localhost/blazing_sql")

# Loop through the selected tables
for table in args.tables:
    parquet_file = f"{table}.parquet"
    print(f"\nExporting table: {table}")

    # Read the table from MySQL
    try:
        df = pd.read_sql(f"SELECT * FROM `{table}`", engine)
    except Exception as e:
        print(f"Error reading table `{table}`: {e}")
        continue

    # Save as Parquet
    try:
        df.to_parquet(parquet_file, index=False, engine="pyarrow")
        print(f"Saved to {parquet_file}")
    except ImportError:
        print("Missing Parquet engine. Install one with: pip install pyarrow")
        sys.exit(1)
    except Exception as e:
        print(f"Error saving `{parquet_file}`: {e}")
