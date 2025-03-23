#!/bin/bash

# Check if the input file is provided as an argument
if [ -z "$1" ]; then
  echo "Usage: $0 <input_csv_file>"
  exit 1
fi

# Input file
input_file="$1"

# Extract the header from the input file
header=$(head -n 1 "$input_file")

# Get the base name of the input file (without directory and extension)
base_name=$(basename "$input_file" .csv)

# Split the input file into chunks of 10 million lines (excluding the header)
tail -n +2 "$input_file" | split -l 10000000 - chunk_

# Add the header back to each chunk and rename the chunk files with the required format
index=1
for f in chunk_*; do
  new_name="chunk_${index}_${base_name}.csv"
  (echo "$header"; cat "$f") > "$new_name"
  rm "$f"  # Clean up the temporary chunk file
  ((index++))
done

echo "Files have been split and saved with the header included."
