import pandas as pd
import argparse

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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean a CSV file by adding column names and enforcing data types.")
    parser.add_argument("input", help="Path to the input CSV file")
    parser.add_argument("output", help="Path to the output CSV file")

    args = parser.parse_args()
    clean_csv(args.input, args.output)
