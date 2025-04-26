import sys
import pandas as pd
from sqlalchemy import create_engine
from pyomnisci import connect


def create_omnisci_table(omnisci, table_name):
    print(f"🛠️ Creating table `{table_name}` in OmniSci...")

    create_table_sql = f"""
    CREATE TABLE {table_name} (
      coordinates INT,
      created_at TIMESTAMP,
      favorited BOOLEAN,
      truncated BOOLEAN,
      tweet_id_str TEXT,
      in_reply_to_user_id_str TEXT,
      tweet_text TEXT,
      tweet_contributors TEXT,
      id BIGINT,
      retweet_count INT,
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
      user_favourites_count INT,
      user_url TEXT,
      user_contributors BOOLEAN,
      user_utc_offset DOUBLE,
      user_id INT,
      user_profile_use_background_image TEXT,
      user_listed_count INT,
      user_protected BOOLEAN,
      user_lang TEXT,
      user_profile_text_color TEXT,
      user_followers_count INT,
      tweet_user_time_zone TEXT,
      user_verified BOOLEAN,
      user_geo_enabled BOOLEAN,
      user_profile_background_color TEXT,
      user_notifications BOOLEAN,
      user_description TEXT,
      user_friends_count INT,
      user_profile_background_image_url TEXT,
      user_statuses_count INT,
      user_screen_name TEXT,
      user_following INT,
      in_reply_to_screen_name TEXT,
      tweet_source TEXT,
      place TEXT,
      in_reply_to_status_id INT,
      favorite_count INT,
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
      numWords INT,
      numCharacters INT,
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

    # Sanitize column names for OmniSci compatibility
    df.columns = [
        col.strip().lower().replace(" ", "_").replace("-", "_")
        for col in df.columns
    ]

    print("📊 Column types:")
    print(df.dtypes)

    # Convert MySQL DATETIME columns to UNIX_TIMESTAMP
    for col in df.columns:
        if df[col].dtype == 'datetime64[ns]':
            print(f"⏳ Converting `{col}` to UNIX_TIMESTAMP...")
            df[col] = df[col].apply(lambda x: int(x.timestamp()) if pd.notnull(x) else None)

    # Drop columns that are completely empty
    df = df.dropna(axis=1, how='all')

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

    # Create table
    create_omnisci_table(omnisci, table_name)

    # Load data into OmniSci
    try:
        print(f"⬆️ Loading data into OmniSci table `{table_name}`...")
        omnisci.load_table(table_name, df)
        print("✅ Import successful.")
    except Exception as e:
        print(f"❌ Error loading data into OmniSci: {e}")
        sys.exit(1)

    # Compatibility test
    print("\n🧪 Testing columns one by one for compatibility...")
    for col in df.columns:
        try:
            test_df = df[[col]].copy()
            test_df.columns = [col.lower()]
            omnisci.load_table("test_table_temp", test_df, preserve_index=False)
            print(f"✅ Column `{col}` OK")
        except Exception as e:
            print(f"❌ Column `{col}` FAILED: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python mysql_to_omnisci.py <mysql_table_name> [limit]")
        sys.exit(1)

    table_name = sys.argv[1]
    limit = int(sys.argv[2]) if len(sys.argv) == 3 else None
    main(table_name, limit)
