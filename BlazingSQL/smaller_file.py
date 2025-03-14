import pandas as pd

# Load the CSV file
input_file = "input.csv"
output_file = "output.csv"

# Read the first 100 rows
df = pd.read_csv(input_file, nrows=100)

# Save to a new CSV file
df.to_csv(output_file, index=False)

print(f"First 100 rows saved to {output_file}")