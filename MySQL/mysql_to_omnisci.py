import sys
import pandas as pd
from sqlalchemy import create_engine
from pyomnisci import connect


def create_omnisci_table(omnisci, table_name):
    print(f"🛠️ Creating table `{table_name}` in OmniSci...")

    try:
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


def main(mysql_table_name, omnisci_table_name, row_limit=None):
    # MySQL connection details
    mysql_user = "root"
    mysql_pass = "root"
    mysql_host = "localhost"
    mysql_port = 3307
    mysql_db = "blazing_sql"

    # OmniSci connection details
    omnisci_user = "admin"
    omnisci_pass = "HyperInteractive"
    omnisci_host = "localhost"
    omnisci_db = "omnisci"

    mysql_url = f"mysql+pymysql://{mysql_user}:{mysql_pass}@{mysql_host}:{mysql_port}/{mysql_db}"
    engine = create_engine(mysql_url)

    query = f"SELECT * FROM blazing_sql.{mysql_table_name}"
    if row_limit is not None:
        query += f" LIMIT {row_limit}"

    print(f"Connecting to MySQL table `blazing_sql.{mysql_table_name}`...")
    try:
        df = pd.read_sql(query, con=engine)
        print(f"✅ Loaded {len(df)} rows from `blazing_sql.{mysql_table_name}`.")
    except Exception as e:
        print(f"❌ Error loading table from MySQL: {e}")
        sys.exit(1)

    # Ensure proper datetime format for OmniSci
    for date_col in ['created_at', 'user_created_at', 'EST', 'user_created_EST']:
        if date_col in df.columns:
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
            failed_conversion = df[df[date_col].isna()]
            if not failed_conversion.empty:
                print(f"❌ The following rows failed to convert {date_col}:")
                print(failed_conversion)

    # Type mapping
    dtype_mapping = {
        "coordinates": "int32",
        "created_at": "datetime64[ns]",
        "favorited": "bool",
        "truncated": "bool",
        "id": "int64",
        "retweet_count": "int32",
        "retweeted": "bool",
        "user_profile_background_tile": "bool",
        "user_created_at": "datetime64[ns]",
        "user_follow_request_sent": "bool",
        "user_favourites_count": "int32",
        "user_contributors": "bool",
        "user_utc_offset": "float64",
        "user_id": "int32",
        "user_listed_count": "int32",
        "user_protected": "bool",
        "user_followers_count": "int32",
        "user_verified": "bool",
        "user_geo_enabled": "bool",
        "user_notifications": "bool",
        "user_friends_count": "int32",
        "user_statuses_count": "int32",
        "user_following": "int32",
        "in_reply_to_status_id": "int32",
        "favorite_count": "int32",
        "EST": "datetime64[ns]",
        "user_created_EST": "datetime64[ns]",
        "tweetQuarter": "int16",
        "tweetmonth": "int16",
        "tweetyear": "int16",
        "containLink": "bool",
        "numWords": "int32",
        "numCharacters": "int32",
        "col_id": "int64"
    }

    df = df.astype(dtype_mapping)
    print("📊 Column types after casting:")
    print(df.dtypes)

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

    create_omnisci_table(omnisci, omnisci_table_name)

    try:
        print(f"⬆️ Loading data into OmniSci table `{omnisci_table_name}`...")
        omnisci.load_table(omnisci_table_name, df)
        print("✅ Import successful.")
    except Exception as e:
        print(f"❌ Error loading data into OmniSci: {e}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        print("Usage: python mysql_to_omnisci.py <mysql_table_name> <omnisci_table_name> [limit]")
        sys.exit(1)

    mysql_table_name = sys.argv[1]
    omnisci_table_name = sys.argv[2]
    limit = int(sys.argv[3]) if len(sys.argv) == 4 else None
    main(mysql_table_name, omnisci_table_name, limit)
