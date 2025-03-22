import argparse
import re

def process_file(input_file, output_file):
    """Function to read a file, remove occurrences of ',\\N,' and write to a new file."""
    try:
        # Open the input file with a specified encoding
        with open(input_file, 'r', encoding='utf-8', errors='ignore') as infile:
            lines = infile.readlines()

        # Process each line and replace ',\N,' with an empty string
        processed_lines = [line.replace('",\\N,', '",,') for line in lines]

        # Write the processed lines to the output file
        with open(output_file, 'w', encoding='utf-8') as outfile:
            outfile.writelines(processed_lines)

        print(f"Occurrences of ',\\N,' have been removed from {input_file} and saved to {output_file}.")
    except Exception as e:
        print(f"An error occurred: {e}")

def replace_newline_backslash(file_path, output_file_path=None):
    try:
        # Open the file with the correct encoding (utf-8 or another encoding if needed)
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # Replace newline followed by backslash with an empty string
        modified_content = re.sub(r'\n\\', '', content)

        # If output_file_path is provided, write to that file, otherwise overwrite the original
        if output_file_path:
            with open(output_file_path, 'w', encoding='utf-8') as output_file:
                output_file.write(modified_content)
        else:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(modified_content)

        print("Replacement done successfully.")

    except UnicodeDecodeError as e:
        print(f"UnicodeDecodeError: {e}. Try specifying a different encoding.")
    except Exception as e:
        print(f"An error occurred: {e}")

def remove_backslash_newline(file_path, output_path, replacement=' '):
    """
    Removes instances of '\' followed by a newline from a file and replaces with a specified character.

    Parameters:
    - file_path: str, the path to the input file
    - output_path: str, the path to save the modified file
    - replacement: str, the character(s) to replace '\n' with (default is a space)
    """
    try:
        # Open the input file with utf-8 encoding (or latin1 if utf-8 doesn't work)
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # Replace '\n' (backslash followed by newline) with the specified replacement
        content = re.sub(r'\\\n', replacement, content)

        # Write the modified content to the output file
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(content)

        print(f"Occurrences of '\\n' have been removed from {file_path} and saved to {output_path}.")
        print("Replacement done successfully.")

    except UnicodeDecodeError:
        print("Error: The file contains characters that could not be decoded with 'utf-8' encoding.")
    except Exception as e:
        print(f"An error occurred: {e}")


def remove_newline_if_no_quote(file_path):
    try:
        # Open the file in read mode with the UTF-8 encoding
        with open(file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()

        # Open the file in write mode
        with open(file_path, "w", encoding="utf-8") as file:
            for line in lines:
                # Check if the line does not end with a quotation mark
                if not line.endswith('"'):
                    line = line.rstrip('\n')  # Remove the newline at the end
                file.write(line)

    except UnicodeDecodeError as e:
        print(f"Error reading the file: {e}")
        print("Try a different encoding or check the file for special characters.")


def remove_newline_and_commas(file_path):
    try:
        # Open the file in read mode with the UTF-8 encoding
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()

        # Use regular expression to replace newline followed by two commas with nothing
        content = re.sub(r'\n,,', ',,', content)

        # Open the file in write mode and write the modified content
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(content)

    except UnicodeDecodeError as e:
        print(f"Error reading the file: {e}")
        print("Try a different encoding or check the file for special characters.")

def remove_newline_if_not_starting_with_quote(file_path):
    try:
        # Read the file content
        with open(file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()

        # Process the lines
        modified_lines = []
        for i in range(len(lines)):
            # If the current line does not start with a quote and it's not the first line, merge it with the previous line
            if i > 0 and lines[i].startswith('",,'):
                modified_lines[-1] = modified_lines[-1].rstrip("\n") + lines[i]
            elif i > 0 and not lines[i].startswith('"'):
                modified_lines[-1] = modified_lines[-1].rstrip("\n") + lines[i]
            else:
                modified_lines.append(lines[i])

        # Write the modified content back to the file
        with open(file_path, "w", encoding="utf-8") as file:
            file.writelines(modified_lines)

    except UnicodeDecodeError as e:
        print(f"Error reading the file: {e}")
        print("Try a different encoding or check the file for special characters.")

def replace_dollar_strings(file_path):
    try:
        # Read the file content
        with open(file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()

        # Process each line to replace patterns
        modified_lines = [re.sub(r'"\$.*?,,"\$', ',"$', line) for line in lines]

        # Write the modified content back to the file
        with open(file_path, "w", encoding="utf-8") as file:
            file.writelines(modified_lines)

    except UnicodeDecodeError as e:
        print(f"Error reading the file: {e}")
        print("Try a different encoding or check the file for special characters.")

def remove_lines_not_ending_with_quote(file_path):
    try:
        # Read the file content
        with open(file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()

        # Keep only lines that end with a quotation mark
        modified_lines = [line for line in lines if line.rstrip().endswith('"')]

        # Write the modified content back to the file
        with open(file_path, "w", encoding="utf-8") as file:
            file.writelines(modified_lines)

    except UnicodeDecodeError as e:
        print(f"Error reading the file: {e}")
        print("Try a different encoding or check the file for special characters.")

# Set up argument parser
def main():
    parser = argparse.ArgumentParser(description="Remove characters at the end of each line in a file until a quote (\"), and keep the quote as the last character.")
    parser.add_argument("input_file", help="Path to the input file")
    parser.add_argument("output_file", help="Path to the output file")

    # Parse the arguments
    args = parser.parse_args()

    # Call the function with the provided file paths
    process_file(args.input_file, args.output_file)
    replace_newline_backslash(args.output_file, "tmp.csv")
    remove_backslash_newline("tmp.csv", args.output_file)
    remove_newline_and_commas(args.output_file)
    remove_newline_if_not_starting_with_quote(args.output_file)
    #replace_dollar_strings(args.output_file)
    remove_lines_not_ending_with_quote(args.output_file)

if __name__ == "__main__":
    main()
