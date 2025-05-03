import sys
import pandas as pd
import time
from pyomnisci import connect

# Array for columns of type INTEGER
integer_columns = [
    "coordinates",
    "retweet_count",
    "user_favourites_count",
    "user_id",
    "user_listed_count",
    "user_followers_count",
    "user_friends_count",
    "user_statuses_count",
    "user_following",
    "favorite_count",
    "numWords",
    "numCharacters",
    "in_reply_to_status_id"
]

# Array for columns of type TIMESTAMP
timestamp_columns = [
    "created_at",
    "user_created_at",
    "EST",
    "user_created_EST"
]

# Array for columns of type DOUBLE
double_columns = [
    "user_utc_offset"
]

# Array for columns of type BOOLEAN
boolean_columns = [
    "favorited",
    "truncated",
    "retweeted",
    "user_profile_background_tile",
    "user_follow_request_sent",
    "user_contributors",
    "user_protected",
    "user_verified",
    "user_geo_enabled",
    "user_notifications",
    "containLink"
]


# Array for columns of type TEXT
text_columns = [
    "tweet_id_str",
    "in_reply_to_user_id_str",
    "tweet_text",
    "tweet_contributors",
    "in_reply_to_status_id_str",
    "geo",
    "in_reply_to_user_id",
    "user_profile_sidebar_border_color",
    "user_name",
    "user_profile_sidebar_fill_color",
    "user_profile_image_url",
    "user_location",
    "user_id_str",
    "user_profile_link_color",
    "user_url",
    "user_lang",
    "user_profile_use_background_image",
    "user_profile_text_color",
    "tweet_user_time_zone",
    "user_profile_background_color",
    "user_description",
    "user_profile_background_image_url",
    "user_screen_name",
    "in_reply_to_screen_name",
    "tweet_source",
    "place",
    "screen_name",
    "tweet_lang",
    "screen_name2",
    "screen_name3",
    "screen_name4",
    "tweet_text_adj"
]

# Array for columns of type BIGINT
bigint_columns = [
    "id",
    "col_id"
]

# Array for columns of type SMALLINT
smallint_columns = [
    "tweetQuarter",
    "tweetmonth",
    "tweetyear"
]

def fetch_table_as_dataframe(omnisci, query):
    print("🔄 Executing query: ", query)
    start_time = time.time()
    cursor = omnisci.cursor()
    cursor.execute(query)
    columns = [col.name for col in cursor.description]
    print(f"💬 Columns fetched: {columns}")
    rows = cursor.fetchall()
    end_time = time.time()
    print(f"Data fetch took {end_time - start_time:.2f} seconds. Fetched {len(rows)} rows.")
    return pd.DataFrame(rows, columns=columns)

def create_destination_table(omnisci, table_name):
    print(f"🛠️ Creating table `{table_name}` in OmniSci with coordinates as INTEGER...")

    # Drop the destination table if it already exists
    drop_sql = f"DROP TABLE IF EXISTS {table_name};"
    try:
        omnisci.cursor().execute(drop_sql)
        print(f"🗑️ Dropped existing table `{table_name}` if it existed.")
    except Exception as e:
        print(f"⚠️ Failed to drop table `{table_name}`: {e}")

    # Create the new destination table with coordinates and in_reply_to_user_id_str
    create_sql = f"""
    CREATE TABLE {table_name} (
        coordinates INTEGER,
        created_at TIMESTAMP,
        favorited BOOLEAN,
        truncated BOOLEAN,
        tweet_id_str TEXT,
        in_reply_to_user_id_str TEXT,
        tweet_text TEXT,
        tweet_contributors TEXT,
        id BIGINT,
        retweet_count INTEGER,
        in_reply_to_status_id_str TEXT,
        geo TEXT,
        retweeted BOOLEAN,
        in_reply_to_user_id TEXT,
        user_profile_sidebar_border_color TEXT,
        user_name TEXT,
        user_profile_sidebar_fill_color TEXT,
        user_profile_background_tile BOOLEAN,
        user_profile_image_url TEXT,
        user_location TEXT,
        user_created_at TIMESTAMP,
        user_id_str TEXT,
        user_follow_request_sent BOOLEAN,
        user_profile_link_color TEXT,
        user_favourites_count INTEGER,
        user_url TEXT,
        user_contributors BOOLEAN,
        user_utc_offset DOUBLE,
        user_id INTEGER,
        user_profile_use_background_image TEXT,
        user_listed_count INTEGER,
        user_protected BOOLEAN,
        user_lang TEXT,
        user_profile_text_color TEXT,
        user_followers_count INTEGER,
        tweet_user_time_zone TEXT,
        user_verified BOOLEAN,
        user_geo_enabled BOOLEAN,
        user_profile_background_color TEXT,
        user_notifications BOOLEAN,
        user_description TEXT,
        user_friends_count INTEGER,
        user_profile_background_image_url TEXT,
        user_statuses_count INTEGER,
        user_screen_name TEXT,
        user_following INTEGER,
        in_reply_to_screen_name TEXT,
        tweet_source TEXT,
        place TEXT,
        in_reply_to_status_id INTEGER,
        favorite_count INTEGER,
        screen_name TEXT,
        tweet_lang TEXT,
        screen_name2 TEXT,
        EST TIMESTAMP,
        screen_name3 TEXT,
        user_created_EST TIMESTAMP,
        tweetQuarter SMALLINT,
        tweetmonth SMALLINT,
        tweetyear SMALLINT,
        containLink BOOLEAN,
        numWords INTEGER,
        numCharacters INTEGER,
        screen_name4 TEXT,
        col_id BIGINT,
        tweet_text_adj TEXT
    );
    """

    try:
        omnisci.cursor().execute(create_sql)
        print(f"✅ Table `{table_name}` created successfully.")
    except Exception as e:
        print(f"❌ Failed to create table `{table_name}`: {e}")
        sys.exit(1)

def insert_data_into_table(omnisci, table_name, df):
    print(f"⬆️ Inserting data into table `{table_name}`...")

    # Reorder the dataframe columns to match the table schema
    try:
        table_columns_order = [
            "coordinates",
            "created_at",
            "favorited",
            "truncated",
            "tweet_id_str",
            "in_reply_to_user_id_str",
            "tweet_text",
            "tweet_contributors",
            "id",
            "retweet_count",
            "in_reply_to_status_id_str",
            "geo",
            "retweeted",
            "in_reply_to_user_id",
            "user_profile_sidebar_border_color",
            "user_name",
            "user_profile_sidebar_fill_color",
            "user_profile_background_tile",
            "user_profile_image_url",
            "user_location",
            "user_created_at",
            "user_id_str",
            "user_follow_request_sent",
            "user_profile_link_color",
            "user_favourites_count",
            "user_url",
            "user_contributors",
            "user_utc_offset",
            "user_id",
            "user_profile_use_background_image",
            "user_listed_count",
            "user_protected",
            "user_lang",
            "user_profile_text_color",
            "user_followers_count",
            "tweet_user_time_zone",
            "user_verified",
            "user_geo_enabled",
            "user_profile_background_color",
            "user_notifications",
            "user_description",
            "user_friends_count",
            "user_profile_background_image_url",
            "user_statuses_count",
            "user_screen_name",
            "user_following",
            "in_reply_to_screen_name",
            "tweet_source",
            "place",
            "in_reply_to_status_id",
            "favorite_count",
            "screen_name",
            "tweet_lang",
            "screen_name2",
            "EST",
            "screen_name3",
            "user_created_EST",
            "tweetQuarter",
            "tweetmonth",
            "tweetyear",
            "containLink",
            "numWords",
            "numCharacters",
            "screen_name4",
            "col_id",
            "tweet_text_adj"
        ]

        # Only keep columns that exist in the DataFrame
        ordered_columns = [col for col in table_columns_order if col in df.columns]
        df = df[ordered_columns]

        omnisci.load_table(table_name, df)
        print("✅ Data inserted successfully.")
    except Exception as e:
        print(f"❌ Error inserting data into OmniSci: {e}")
        sys.exit(1)

def get_total_row_count(omnisci, table_name):
    query = f"SELECT COUNT(*) FROM {table_name};"
    cursor = omnisci.cursor()
    cursor.execute(query)
    count = cursor.fetchone()[0]
    return count

def main(source_table, target_table, chunk_size=1_000_000):
    omnisci_user = "admin"
    omnisci_pass = "HyperInteractive"
    omnisci_host = "localhost"
    omnisci_db = "omnisci"

    print(f"🔌 Connecting to OmniSci DB `{omnisci_db}`...")
    try:
        omnisci = connect(
            user=omnisci_user,
            password=omnisci_pass,
            host=omnisci_host,
            dbname=omnisci_db
        )
        print("✅ Connected to OmniSci.")
    except Exception as e:
        print(f"❌ Could not connect to OmniSci: {e}")
        sys.exit(1)

    create_destination_table(omnisci, target_table)

    offset = 0
    total_inserted = 0

    total_rows = get_total_row_count(omnisci, source_table)
    print(f"📊 Total rows to process: {total_rows}")

    offset = 0
    total_inserted = 0

    while offset < total_rows:
        query = f"SELECT * FROM {source_table} LIMIT {chunk_size} OFFSET {offset}"
        print(f"\n📥 Fetching chunk: OFFSET {offset}, LIMIT {chunk_size}...")
        try:
            df = fetch_table_as_dataframe(omnisci, query)
        except Exception as e:
            print(f"❌ Error fetching data: {e}")
            break

        if df.empty:
            print("✅ All data has been processed.")
            break

        # Select only the columns we support
        all_columns_to_copy = (
            integer_columns + timestamp_columns + boolean_columns +
            text_columns + bigint_columns + smallint_columns + double_columns
        )
        existing_columns = [col for col in all_columns_to_copy if col in df.columns]
        df_to_insert = df[existing_columns].copy()

        # Data type handling (same logic as before)
        for field in integer_columns:
            if field in df_to_insert:
                df_to_insert[field] = pd.to_numeric(df_to_insert[field], errors='coerce').fillna(0).astype('int32')
        for field in text_columns:
            if field in df_to_insert:
                df_to_insert[field] = df_to_insert[field].astype(str)
        for field in boolean_columns:
            if field in df_to_insert:
                df_to_insert[field] = df_to_insert[field].astype(bool)
        for field in timestamp_columns:
            if field in df_to_insert:
                df_to_insert[field] = pd.to_datetime(df_to_insert[field], errors='coerce')
        for field in bigint_columns:
            if field in df_to_insert:
                df_to_insert[field] = pd.to_numeric(df_to_insert[field], errors='coerce').fillna(0).astype('int64')
        for field in smallint_columns:
            if field in df_to_insert:
                df_to_insert[field] = pd.to_numeric(df_to_insert[field], errors='coerce').fillna(0).astype('int16')
        for field in double_columns:
            if field in df_to_insert:
                df_to_insert[field] = pd.to_numeric(df_to_insert[field], errors='coerce').fillna(0).astype('float64')

        print("🧪 Inserting chunk into OmniSci...")
        try:
            insert_data_into_table(omnisci, target_table, df_to_insert)
            inserted_count = len(df_to_insert)
            total_inserted += inserted_count
            print(f"✅ Inserted {inserted_count} rows. Total inserted: {total_inserted}")
            print(f"📈 Progress: {(100 * total_inserted / total_rows):.2f}%")
        except Exception as e:
            print(f"❌ Failed to insert chunk: {e}")
            break

        offset += chunk_size

    print(f"\n🎉 Finished. Total rows inserted: {total_inserted}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python test_column_imports.py <source_table> <destination_table>")
        sys.exit(1)

    source_table = sys.argv[1]
    target_table = sys.argv[2]

    main(source_table, target_table)
