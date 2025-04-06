import csv
import argparse

def clean_csv(input_file, output_file):
    with open(input_file, mode='r', newline='', encoding='utf-8', errors='ignore') as infile:
        reader = csv.reader(infile)

        with open(output_file, mode='w', newline='', encoding='utf-8') as outfile:
            writer = csv.writer(outfile, quotechar='"', quoting=csv.QUOTE_MINIMAL)

            for row_index, row in enumerate(reader):
                cleaned_row = []
                for item in row:
                    # Replace single quotes with space, commas with space, and remove double quotes
                    cleaned_item = item.replace("'", " ").replace(',', " ").replace('"', "")
                    if row_index == 0:
                        cleaned_row.append(cleaned_item)
                    else:
                        cleaned_row.append(f"'{cleaned_item}'")

                writer.writerow(cleaned_row)

def main():
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description="Clean CSV by replacing ' and , with blank space and wrap each field in double quotes.")
    parser.add_argument('input_file', help="The path to the input CSV file")
    parser.add_argument('output_file', help="The path to the output CSV file")

    # Parse the arguments
    args = parser.parse_args()

    # Call the function to clean the CSV file
    clean_csv(args.input_file, args.output_file)

    print(f"Processed file saved as '{args.output_file}'")

if __name__ == "__main__":
    main()
