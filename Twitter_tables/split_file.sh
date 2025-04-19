#!/bin/bash

# Check if the input file and chunk count are provided as arguments
if [ -z "$1" ] || [ -z "$2" ]; then
  echo "Usage: $0 <input_csv_file> <num_chunks>"
  exit 1
fi

# Input file and number of chunks
input_file="$1"
num_chunks="$2"

# Extract the header from the input file
header=$(head -n 1 "$input_file")
base_name=$(basename "$input_file" .csv)

# Get total lines excluding the header
total_lines=$(($(wc -l < "$input_file") - 1))

# Calculate lines per split (last one might have a few more)
lines_per_file=$(( (total_lines + num_chunks - 1) / num_chunks ))

# Split the file
tail -n +2 "$input_file" | split -l "$lines_per_file" - chunk_

# Add headers back to each chunk and rename them
index=1
for f in chunk_*; do
  new_name="chunk_${index}_${num_chunks}_${base_name}.csv"
  (echo "$header"; cat "$f") > "$new_name"
  rm "$f"  # Clean up the temporary chunk file
  ((index++))
done

echo "Files have been split into $num_chunks chunks."
