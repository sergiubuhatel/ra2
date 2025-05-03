#!/bin/bash

# Array of years to process
years=(2018 2019 2020 2021 2022 2023)

# Loop through each year and run the script
for year in "${years[@]}"; do
    echo "🚀 Processing tweets_$year → Twitter_$year"
    python fix_column_types.py "tweets_$year" "Twitter_$year"
done
