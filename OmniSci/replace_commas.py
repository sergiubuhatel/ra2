import csv
import re
import argparse


def remove_null_characters(input_file):
    with open(input_file, mode='rb') as infile:
        data = infile.read()
    # Remove any null bytes (NUL characters)
    cleaned_data = data.replace(b'\x00', b'')
    return cleaned_data


def replace_commas_in_quotes(input_file, output_file):
    # Read the cleaned data from the file
    cleaned_data = remove_null_characters(input_file)

    # Open a temporary file to write the cleaned data and process it
    with open('cleaned_temp.csv', mode='wb') as temp_file:
        temp_file.write(cleaned_data)

    # Open the cleaned CSV file for processing
    with open('cleaned_temp.csv', mode='r', newline='', encoding='utf-8') as infile:
        reader = csv.reader(infile)
        rows = []

        # Iterate over each row in the CSV file
        for row in reader:
            new_row = []
            for cell in row:
                # Use regular expression to find and replace commas inside quotes
                new_cell = re.sub(r'(?<=")[^"]*,[^"]*(?=")', lambda match: match.group(0).replace(',', ' '), cell)
                # Ensure the cell is enclosed in double quotes
                if cell != new_cell:
                    new_cell = f'"{new_cell}"'  # Add quotes around modified content
                else:
                    new_cell = f'"{cell}"'  # Enclose the original content in quotes
                new_row.append(new_cell)
            rows.append(new_row)

    # Write the modified rows back to the output CSV file
    with open(output_file, mode='w', newline='', encoding='utf-8') as outfile:
        writer = csv.writer(outfile, quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerows(rows)


def main():
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description="Replace commas inside quotes with spaces in a CSV file.")
    parser.add_argument("input_file", help="Path to the input CSV file")
    parser.add_argument("output_file", help="Path to the output CSV file")

    # Parse the command-line arguments
    args = parser.parse_args()

    # Call the function to replace commas in quoted strings
    replace_commas_in_quotes(args.input_file, args.output_file)


if __name__ == "__main__":
    main()
