#
# Example:
# python export_to_csv.py tweets_2017 tweets_2018 tweets_2019 tweets_2020 tweets_2021 tweets_2022 tweets_2023
#

import pandas as pd
import sqlalchemy
import argparse
import sys
import csv

# Set up command-line argument parsing
parser = argparse.ArgumentParser(description="Export selected MySQL tables to pipe-delimited CSV files with UTF-8 encoding and LF line endings.")
parser.add_argument("tables", nargs="+", help="List of MySQL tables to export")
args = parser.parse_args()

# Connect to MySQL
engine = sqlalchemy.create_engine("mysql+pymysql://root:root@localhost/blazing_sql")

# Loop through the selected tables
for table in args.tables:
    csv_file = f"{table}.csv"
    print(f"\nExporting table: {table}")

    # Read the table from MySQL
    try:
        df = pd.read_sql(f"SELECT * FROM `{table}`", engine)
    except Exception as e:
        print(f"❌ Error reading table `{table}`: {e}")
        continue

    # Save CSV with pipe delimiter, UTF-8 encoding, LF line endings, and double quotes for quoting
    try:
        with open(csv_file, "w", encoding="utf-8", newline="\n") as f:
            df.to_csv(
                f,
                index=False,
                sep="|",
                header=True,
                line_terminator="\n",  # Ensures LF line endings between rows only
                quoting=csv.QUOTE_MINIMAL,  # Only quote when necessary
                quotechar='"',  # Use double quotes for quoting fields
                escapechar="\\",  # Escape special characters, like single quotes
                quote_fields=True  # Prevents data from being split into multiple lines inside fields
            )
        print(f"✅ Saved to {csv_file} (UTF-8, LF line endings, pipe-delimited, double-quoted fields)")
    except Exception as e:
        print(f"❌ Error saving `{csv_file}`: {e}")
