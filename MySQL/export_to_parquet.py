import pandas as pd
import sqlalchemy
import argparse

# Set up command-line argument parsing
parser = argparse.ArgumentParser(description="Export a MySQL table to a Parquet file.")
parser.add_argument("table_name", help="Name of the MySQL table to export")
parser.add_argument("parquet_file", help="Output Parquet file name")
args = parser.parse_args()

# Connect to MySQL
engine = sqlalchemy.create_engine("mysql+pymysql://root:root@localhost/blazing_sql")

# Read table from MySQL
df = pd.read_sql(f"SELECT * FROM {args.table_name}", engine)

# Print first 5 rows
print("First 5 rows of the DataFrame:")
print(df.head())

# Save DataFrame as Parquet
df.to_parquet(args.parquet_file, index=False)
print(f"\nData exported to {args.parquet_file}")
