#!/bin/bash

# Check if the correct number of arguments are passed
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <year>"
    exit 1
fi

# Assign command-line argument (year) to variable
year=$1

# Step 1: Take the first 100 lines of the input file (Twitter_${year}.csv) and store it in tmp_1.csv
head -n 100 "Twitter_${year}.csv" > tmp_1.csv

# Step 2: Process tmp_1.csv to remove trailing backslashes in lines
awk '{if (substr($0, length, 1) == "\\") {printf "%s", substr($0, 1, length-1)} else {print $0}}' tmp_1.csv > tmp_2.csv

# Step 3: Combine header file (headers.csv) with tmp_2.csv into tmp_1.csv
cat headers.csv tmp_2.csv > tmp_1.csv

# Step 4: Run the Python script to process the modified file and save the result to the output file
python process_file.py tmp_1.csv "fixed_Twitter_${year}.csv"

# Step 5: Clean up temporary files
rm tmp_*.csv