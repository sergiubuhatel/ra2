#!/usr/bin/env python3
import pandas as pd
import os

# ---------------------------
# Paths
# ---------------------------
csv_file = "/data/retweet_network2017.csv"
parquet_root = "/data/retweets_parquet"

# Create output folder if missing
os.makedirs(parquet_root, exist_ok=True)

# ---------------------------
# Read CSV safely
# ---------------------------
print("Loading CSV (this may take a while)...")

df = pd.read_csv(
    csv_file,
    header=None,
    names=["company", "edgeA", "edgeB", "year", "month", "timestamp"],
    dtype=str,
    engine="python",          # Use Python engine to handle bad rows
    on_bad_lines="skip",      # Skip malformed lines
)

print(f"Rows loaded: {len(df)}")

# ---------------------------
# Clean and parse timestamps
# ---------------------------
df["timestamp"] = pd.to_datetime(
    df["timestamp"].str.strip(),
    format="%Y-%m-%d %H:%M:%S",
    errors="coerce"           # Turn unparseable dates into NaT
)

bad_ts_count = df["timestamp"].isna().sum()
print(f"Rows with bad timestamps: {bad_ts_count}")

# Drop rows with bad timestamps
df = df.dropna(subset=["timestamp"])
print(f"Rows after dropping bad timestamps: {len(df)}")

# ---------------------------
# Convert numeric columns
# ---------------------------
df["year"] = df["year"].astype("int32")
df["month"] = df["month"].astype("int32")

# ---------------------------
# Write to Parquet
# ---------------------------
print("Writing Parquet files...")
df.to_parquet(
    parquet_root,
    engine="pyarrow",
    partition_cols=["company", "year", "month"],
    index=False
)

print(f"Parquet dataset written to: {parquet_root}")
