import sys
import pandas as pd
from sqlalchemy import create_engine
from pyomnisci import connect


def create_omnisci_table(omnisci, table_name):
    print(f"🛠️ Creating table `{table_name}` in OmniSci...")

    try:
        # Drop the table if it already exists
        omnisci.cursor().execute(f"DROP TABLE IF EXISTS {table_name};")
        print(f"🗑️ Dropped existing table `{table_name}`.")
    except Exception as e:
        print(f"⚠️ Could not drop existing table `{table_name}`: {e}")

    create_table_sql = f"""
    CREATE TABLE {table_name} (
      coordinates INTEGER,
      created_at TIMESTAMP(0),
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
      user_created_at TIMESTAMP(0),
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
      EST TIMESTAMP(0),
      screen_name3 TEXT,
      user_created_EST TIMESTAMP(0),
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
        omnisci.cursor().execute(create_table_sql)
        print(f"✅ Table `{table_name}` created successfully.")
    except Exception as e:
        print(f"❌ Failed to create table `{table_name}`: {e}")


def main(table_name, row_limit=None):
    # MySQL connection details
    mysql_user = "root"
    mysql_pass = "root"
    mysql_host = "localhost"
    mysql_port = 3307  # via SSH tunnel
    mysql_db = "blazing_sql"

    # OmniSci connection details
    omnisci_user = "admin"
    omnisci_pass = "HyperInteractive"
    omnisci_host = "localhost"
    omnisci_db = "omnisci"

    # Create SQLAlchemy engine for MySQL
    mysql_url = f"mysql+pymysql://{mysql_user}:{mysql_pass}@{mysql_host}:{mysql_port}/{mysql_db}"
    engine = create_engine(mysql_url)

    # Construct query
    query = f"SELECT * FROM blazing_sql.{table_name}"
    if row_limit is not None:
        query += f" LIMIT {row_limit}"

    print(f"Connecting to MySQL table `blazing_sql.{table_name}`...")
    try:
        df = pd.read_sql(query, con=engine)
        print(f"✅ Loaded {len(df)} rows from `blazing_sql.{table_name}`.")
    except Exception as e:
        print(f"❌ Error loading table from MySQL: {e}")
        sys.exit(1)

    # Ensure `created_at`, `user_created_at`, and `EST` columns are converted to UNIX timestamps
    for date_col in ['created_at', 'user_created_at', 'EST', 'user_created_EST']:
        if date_col in df.columns:
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')  # Convert to datetime
            df[date_col] = df[date_col].astype('int64') // 10**9  # Convert to UNIX timestamp in seconds

            # Check if any NaT values exist (conversion failed)
            failed_conversion = df[df[date_col].isna()]
            if not failed_conversion.empty:
                print(f"❌ The following rows failed to convert {date_col}:")
                print(failed_conversion)

    # Define OmniSci to Pandas type mapping
    dtype_mapping = {
        "coordinates": "int32",
        "created_at": "int64",  # UNIX timestamp in seconds
        "favorited": "bool",
        "truncated": "bool",
        "tweet_id_str": "object",
        "in_reply_to_user_id_str": "object",
        "tweet_text": "object",
        "tweet_contributors": "object",
        "id": "int64",
        "retweet_count": "int32",
        "in_reply_to_status_id_str": "object",
        "geo": "object",
        "retweeted": "bool",
        "in_reply_to_user_id": "object",
        "user_profile_sidebar_border_color": "object",
        "user_name": "object",
        "user_profile_sidebar_fill_color": "object",
        "user_profile_background_tile": "bool",
        "user_profile_image_url": "object",
        "user_location": "object",
        "user_created_at": "int64",  # UNIX timestamp in seconds
        "user_id_str": "object",
        "user_follow_request_sent": "bool",
        "user_profile_link_color": "object",
        "user_favourites_count": "int32",
        "user_url": "object",
        "user_contributors": "bool",
        "user_utc_offset": "float64",
        "user_id": "int32",
        "user_profile_use_background_image": "object",
        "user_listed_count": "int32",
        "user_protected": "bool",
        "user_lang": "object",
        "user_profile_text_color": "object",
        "user_followers_count": "int32",
        "tweet_user_time_zone": "object",
        "user_verified": "bool",
        "user_geo_enabled": "bool",
        "user_profile_background_color": "object",
        "user_notifications": "bool",
        "user_description": "object",
        "user_friends_count": "int32",
        "user_profile_background_image_url": "object",
        "user_statuses_count": "int32",
        "user_screen_name": "object",
        "user_following": "int32",
        "in_reply_to_screen_name": "object",
        "tweet_source": "object",
        "place": "object",
        "in_reply_to_status_id": "int32",
        "favorite_count": "int32",
        "screen_name": "object",
        "tweet_lang": "object",
        "screen_name2": "object",
        "EST": "int64",  # UNIX timestamp in seconds
        "screen_name3": "object",
        "user_created_EST": "int64",  # UNIX timestamp in seconds
        "tweetQuarter": "int16",
        "tweetmonth": "int16",
        "tweetyear": "int16",
        "containLink": "bool",
        "numWords": "int32",
        "numCharacters": "int32",
        "screen_name4": "object",
        "col_id": "int64",
        "tweet_text_adj": "object"
    }

    # Cast the DataFrame types based on the mapping
    df = df.astype(dtype_mapping)

    print("📊 Column types after casting:")
    print(df.dtypes)

    # Connect to OmniSci
    try:
        print(f"🔌 Connecting to OmniSci DB `{omnisci_db}`...")
        omnisci = connect(
            user=omnisci_user,
            password=omnisci_pass,
            host=omnisci_host,
            dbname=omnisci_db
        )
    except Exception as e:
        print(f"❌ Error connecting to OmniSci: {e}")
        sys.exit(1)

    # Create the target table
    create_omnisci_table(omnisci, table_name)

    # Load into OmniSci
    try:
        print(f"⬆️ Loading data into OmniSci table `{table_name}`...")
        omnisci.load_table(table_name, df)
        print("✅ Import successful.")
    except Exception as e:
        print(f"❌ Error loading data into OmniSci: {e}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python mysql_to_omnisci.py <mysql_table_name> [limit]")
        sys.exit(1)

    table_name = sys.argv[1]
    limit = int(sys.argv[2]) if len(sys.argv) == 3 else None
    main(table_name, limit)
