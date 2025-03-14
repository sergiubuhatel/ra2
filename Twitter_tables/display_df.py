import pandas as pd
import argparse

def display_first_rows(input_file):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(input_file)

    # Display the first 5 rows of the DataFrame
    print(df.head())

if __name__ == "__main__":
    # Set up the argument parser
    parser = argparse.ArgumentParser(description="Read a CSV file and display the first 5 rows.")
    parser.add_argument("input", help="Path to the input CSV file")  # Command-line argument for input file

    # Parse the arguments
    args = parser.parse_args()

    # Call the function to display the first 5 rows
    display_first_rows(args.input)