import sys
import pandas as pd
from pyomnisci import connect


def create_omnisci_table(omnisci, table_name, columns_and_types):
    print(f"🛠️ Creating table `{table_name}` in OmniSci...")

    try:
        omnisci.cursor().execute(f"DROP TABLE IF EXISTS {table_name};")
        print(f"🗑️ Dropped existing table `{table_name}`.")
    except Exception as e:
        print(f"⚠️ Could not drop existing table `{table_name}`: {e}")

    column_defs = ",\n".join([f"{col} {col_type}" for col, col_type in columns_and_types])
    create_sql = f"CREATE TABLE {table_name} (\n{column_defs}\n);"

    try:
        omnisci.cursor().execute(create_sql)
        print(f"✅ Table `{table_name}` created successfully.")
    except Exception as e:
        print(f"❌ Failed to create table `{table_name}`: {e}")
        sys.exit(1)


def fetch_table_as_dataframe(omnisci, query):
    cursor = omnisci.cursor()
    cursor.execute(query)
    columns = [col.name for col in cursor.description]
    rows = cursor.fetchall()
    return pd.DataFrame(rows, columns=columns)


def main(source_table, target_table, row_limit=None):
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
    except Exception as e:
        print(f"❌ Could not connect to OmniSci: {e}")
        sys.exit(1)

    query = f"SELECT * FROM {source_table}"
    if row_limit:
        query += f" LIMIT {row_limit}"
    print(f"`{query}`")

    print(f"📥 Loading data from OmniSci table `{source_table}`...")
    try:
        df = fetch_table_as_dataframe(omnisci, query)
        print(f"✅ Loaded {len(df)} rows.")
    except Exception as e:
        print(f"❌ Failed to load data from OmniSci: {e}")
        sys.exit(1)

    # Define schema
    columns_and_types = [
        ("coordinates", "FLOAT"),
        ("created_at", "TIMESTAMP"),
        ("favorited", "BOOLEAN"),
        ("truncated", "BOOLEAN"),
        ("tweet_id_str", "TEXT"),
        ("in_reply_to_user_id_str", "TEXT"),
        ("tweet_text", "TEXT"),
        ("tweet_contributors", "TEXT"),
        ("id", "BIGINT"),
        ("retweet_count", "INT"),
        ("in_reply_to_status_id_str", "TEXT"),
        ("geo", "TEXT"),
        ("retweeted", "BOOLEAN"),
        ("in_reply_to_user_id", "TEXT"),
        ("user_profile_sidebar_border_color", "TEXT"),
        ("user_name", "TEXT"),
        ("user_profile_sidebar_fill_color", "TEXT"),
        ("user_profile_background_tile", "BOOLEAN"),
        ("user_profile_image_url", "TEXT"),
        ("user_location", "TEXT"),
        ("user_created_at", "TIMESTAMP"),
        ("user_id_str", "TEXT"),
        ("user_follow_request_sent", "BOOLEAN"),
        ("user_profile_link_color", "TEXT"),
        ("user_favourites_count", "INT"),
        ("user_url", "TEXT"),
        ("user_contributors", "BOOLEAN"),
        ("user_utc_offset", "DOUBLE"),
        ("user_id", "INT"),
        ("user_profile_use_background_image", "TEXT"),
        ("user_listed_count", "INT"),
        ("user_protected", "BOOLEAN"),
        ("user_lang", "TEXT"),
        ("user_profile_text_color", "TEXT"),
        ("user_followers_count", "INT"),
        ("tweet_user_time_zone", "TEXT"),
        ("user_verified", "BOOLEAN"),
        ("user_geo_enabled", "BOOLEAN"),
        ("user_profile_background_color", "TEXT"),
        ("user_notifications", "BOOLEAN"),
        ("user_description", "TEXT"),
        ("user_friends_count", "INT"),
        ("user_profile_background_image_url", "TEXT"),
        ("user_statuses_count", "INT"),
        ("user_screen_name", "TEXT"),
        ("user_following", "INT"),
        ("in_reply_to_screen_name", "TEXT"),
        ("tweet_source", "TEXT"),
        ("place", "TEXT"),
        ("in_reply_to_status_id", "INT"),
        ("favorite_count", "INT"),
        ("screen_name", "TEXT"),
        ("tweet_lang", "TEXT"),
        ("screen_name2", "TEXT"),
        ("EST", "TIMESTAMP"),
        ("screen_name3", "TEXT"),
        ("user_created_EST", "TIMESTAMP"),
        ("tweetQuarter", "SMALLINT"),
        ("tweetmonth", "SMALLINT"),
        ("tweetyear", "SMALLINT"),
        ("containLink", "BOOLEAN"),
        ("numWords", "INT"),
        ("numCharacters", "INT"),
        ("screen_name4", "TEXT"),
        ("col_id", "BIGINT"),
        ("tweet_text_adj", "TEXT")
    ]

    # Create new table
    create_omnisci_table(omnisci, target_table, columns_and_types)

    # Type conversions
    for col, col_type in columns_and_types:
        if col not in df.columns:
            continue
        if col_type == "TIMESTAMP":
            df[col] = pd.to_datetime(df[col], errors='coerce')
            df[col] = df[col].astype("int64") // 10**9
        elif col_type in ("INT", "BIGINT"):
            df[col] = pd.to_numeric(df[col], errors='coerce', downcast='integer')
        elif col_type in ("FLOAT", "DOUBLE"):
            df[col] = pd.to_numeric(df[col].astype(str), errors='coerce')
            df[col] = df[col].astype(float)
        elif col_type == "BOOLEAN":
            df[col] = df[col].astype(bool)

    # Debug: check for any columns with invalid float values
    for col, col_type in columns_and_types:
        if col_type in ("FLOAT", "DOUBLE") and col in df.columns:
            invalid_vals = df[~df[col].apply(lambda x: isinstance(x, float) or pd.isna(x))][col]
            if not invalid_vals.empty:
                print(f"⚠️ Column `{col}` contains non-float values that may cause issues:")
                print(invalid_vals.head(5))

    print(f"⬆️ Loading data into OmniSci table `{target_table}`...")
    try:
        omnisci.load_table(target_table, df)
        print("✅ Import successful.")
    except Exception as e:
        print(f"❌ Error loading data into OmniSci: {e}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python cast_from_table.py <source_table> <target_table> [limit]")
        sys.exit(1)

    source_table = sys.argv[1]
    target_table = sys.argv[2]
    limit = int(sys.argv[3]) if len(sys.argv) == 4 else None

    main(source_table, target_table, limit)
