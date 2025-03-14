import argparse
import string

# Function to process the lines in the file
def process_file(input_file, output_file):
    # Open the input file for reading
    with open(input_file, 'r', encoding='utf-8', errors='ignore') as infile:
        lines = infile.readlines()

    # Open the output file for writing
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for line in lines:
            # Strip off characters from the end until a '"' is found
            index = line.rfind('"')  # Find the last occurrence of '"'
            if index != -1:
                # Keep the part up to and including the last '"'
                modified_line = line[:index+1]
            else:
                modified_line = line  # If no '"' found, keep the whole line as is

            # Write the modified line to the output file, ensuring special characters are handled
            outfile.write(modified_line)

# Set up argument parser
def main():
    parser = argparse.ArgumentParser(description="Remove characters at the end of each line in a file until a quote (\"), and keep the quote as the last character, handling special characters.")
    parser.add_argument("input_file", help="Path to the input file")
    parser.add_argument("output_file", help="Path to the output file")

    # Parse the arguments
    args = parser.parse_args()

    # Call the function with the provided file paths
    process_file(args.input_file, args.output_file)

if __name__ == "__main__":
    main()
