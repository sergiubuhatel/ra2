import argparse
import re
import pandas as pd
from time import sleep
import shutil
import os

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


# Define column names and data types
columns = [
    "coordinates", "created_at", "favorited", "truncated", "tweet_id_str", "in_reply_to_user_id_str",
    "tweet_text", "tweet_contributors", "id", "retweet_count", "in_reply_to_status_id_str", "geo",
    "retweeted", "in_reply_to_user_id", "user_profile_sidebar_border_color", "user_name",
    "user_profile_sidebar_fill_color", "user_profile_background_tile", "user_profile_image_url",
    "user_location", "user_created_at", "user_id_str", "user_follow_request_sent",
    "user_profile_link_color", "user_favourites_count", "user_url", "user_contributors",
    "user_utc_offset", "user_id", "user_profile_use_background_image", "user_listed_count",
    "user_protected", "user_lang", "user_profile_text_color", "user_followers_count",
    "tweet_user_time_zone", "user_verified", "user_geo_enabled", "user_profile_background_color",
    "user_notifications", "user_description", "user_friends_count",
    "user_profile_background_image_url", "user_statuses_count", "user_screen_name",
    "user_following", "in_reply_to_screen_name", "tweet_source", "place", "in_reply_to_status_id",
    "favorite_count", "screen_name", "tweet_lang", "screen_name2", "EST", "screen_name3",
    "user_created_EST", "tweetQuarter", "tweetmonth", "tweetyear", "containLink", "numWords",
    "numCharacters", "screen_name4", "col_id", "tweet_text_adj"
]

dtypes = {
    "coordinates": "Int64",
    "created_at": "datetime64[ns]",
    "favorited": "boolean",
    "truncated": "boolean",
    "tweet_id_str": "string",
    "in_reply_to_user_id_str": "string",
    "tweet_text": "string",
    "tweet_contributors": "string",
    "id": "Int64",
    "retweet_count": "Int64",
    "in_reply_to_status_id_str": "string",
    "geo": "string",
    "retweeted": "boolean",
    "in_reply_to_user_id": "string",
    "user_profile_sidebar_border_color": "string",
    "user_name": "string",
    "user_profile_sidebar_fill_color": "string",
    "user_profile_background_tile": "boolean",
    "user_profile_image_url": "string",
    "user_location": "string",
    "user_created_at": "datetime64[ns]",
    "user_id_str": "string",
    "user_follow_request_sent": "boolean",
    "user_profile_link_color": "string",
    "user_favourites_count": "Int64",
    "user_url": "string",
    "user_contributors": "boolean",
    "user_utc_offset": "float64",
    "user_id": "Int64",
    "user_profile_use_background_image": "string",
    "user_listed_count": "Int64",
    "user_protected": "boolean",
    "user_lang": "string",
    "user_profile_text_color": "string",
    "user_followers_count": "Int64",
    "tweet_user_time_zone": "string",
    "user_verified": "boolean",
    "user_geo_enabled": "boolean",
    "user_profile_background_color": "string",
    "user_notifications": "boolean",
    "user_description": "string",
    "user_friends_count": "Int64",
    "user_profile_background_image_url": "string",
    "user_statuses_count": "Int64",
    "user_screen_name": "string",
    "user_following": "Int64",
    "in_reply_to_screen_name": "string",
    "tweet_source": "string",
    "place": "string",
    "in_reply_to_status_id": "Int64",
    "favorite_count": "Int64",
    "screen_name": "string",
    "tweet_lang": "string",
    "screen_name2": "string",
    "EST": "datetime64[ns]",
    "screen_name3": "string",
    "user_created_EST": "datetime64[ns]",
    "tweetQuarter": "Int64",
    "tweetmonth": "Int64",
    "tweetyear": "Int64",
    "containLink": "boolean",
    "numWords": "Int64",
    "numCharacters": "Int64",
    "screen_name4": "string",
    "col_id": "Int64",
    "tweet_text_adj": "string"
}


# Define the list of datetime columns
datetime_columns = ["created_at", "user_created_at", "EST", "user_created_EST"]

def clean_csv(input_file, output_file):
    try:
        # Read CSV without headers, without dtype and datetime parsing to inspect the raw data
        df = pd.read_csv(input_file, header=None, na_values=["", "NA", "NULL"], low_memory=False)

        # Show the first few rows to check how data is being read
        print("Sample data from the file:")
        print(df.head())

        # Manually specify columns and types if needed after inspecting the data
        df.columns = columns

        # Manually force conversion for datetime columns
        for col in datetime_columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')

        # Check if there are any issues with datetime conversion
        for col in datetime_columns:
            if df[col].isnull().any():
                print(f"Warning: Some entries in {col} could not be parsed as datetime.")

        # Save cleaned CSV
        df.to_csv(output_file, index=False)
        print(f"Processed file saved as {output_file}")

    except Exception as e:
        print(f"Error processing file: {e}")

def display_first_rows(input_file):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(input_file)

    # Display the first 5 rows of the DataFrame
    print(df.head())

def get_tmp_file_name(args):
    return "tmp_" + args.output_file

def rename_file(old_file, new_file):
    # Remove new_file if it exists
    if os.path.exists(new_file):
        os.remove(new_file)

    # Rename file
    os.rename(old_file, new_file)

# Set up argument parser
def main():
    parser = argparse.ArgumentParser(description="Remove characters at the end of each line in a file until a quote (\"), and keep the quote as the last character.")
    parser.add_argument("input_file", help="Path to the input file")
    parser.add_argument("output_file", help="Path to the output file")

    # Parse the arguments
    args = parser.parse_args()

    # Get tmp file name
    tmp_file_name = get_tmp_file_name(args)

    # Call the function with the provided file paths
    print("\nStep 1 - process_file")
    process_file(args.input_file, args.output_file)

    print("\nStep 2 - replace_newline_backslash")
    replace_newline_backslash(args.output_file, tmp_file_name)

    print("\nStep 3 - remove_backslash_newline")
    remove_backslash_newline(tmp_file_name, args.output_file)

    print("\nStep 4 - remove_newline_and_commas")
    remove_newline_and_commas(args.output_file)

    print("\nStep 5 - remove_newline_if_not_starting_with_quote")
    remove_newline_if_not_starting_with_quote(args.output_file)

    print("\nStep 6 - remove_newline_if_not_starting_with_quote")
    remove_lines_not_ending_with_quote(args.output_file)

    sleep(5)
    print("\nStep 7 - clean_csv")
    clean_csv(args.output_file, tmp_file_name)

    # Copy the source file to the destination
    print("\nStep 8 - rename_file")
    rename_file(tmp_file_name, args.output_file)

    sleep(5)
    print("\nStep 9 - display_first_rows")
    display_first_rows(args.output_file)

    print("\nDone")

if __name__ == "__main__":
    main()
