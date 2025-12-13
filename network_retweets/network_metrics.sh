#!/bin/bash

# List of years
YEARS=(2017 2018 2019 2020 2021 2022 2023)

# Loop through each year and run the Python script
for YEAR in "${YEARS[@]}"; do
    echo "Running GPU network analysis for year $YEAR..."
    python network_metrics_gpu.py --year "$YEAR"
    echo "Finished year $YEAR"
done

echo "All years completed."
