#!/bin/bash

# Check if the correct number of arguments are passed
if [ "$#" -ne 1 ]; then
	    echo "Usage: $0 <year>"
	        exit 1
fi

# Assign command-line argument (year) to variable
year=$1

# Step 1: Process tmp_1.csv to remove trailing backslashes in lines
awk '{if (substr($0, length, 1) == "\\") {printf "%s", substr($0, 1, length-1)} else {print $0}}' "Twitter_${year}.csv" > tmp_1.csv

# Step 2: Combine header file (headers.csv) with tmp_2.csv into tmp_1.csv
cat headers.csv tmp_1.csv > "fixed_Twitter_${year}.csv"

# Step 3: Clean up temporary files
rm tmp_*.csv
