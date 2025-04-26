import sys
import pandas as pd
from sqlalchemy import create_engine
from pyomnisci import connect


def main(table_name, row_limit=None):
    # Setup MySQL connection
    mysql_url = "mysql+pymysql://root:root@localhost:3307/blazing_sql"
    engine = create_engine(mysql_url)

    # Setup OmniSci connection
    omnisci = connect(
        user="admin",
        password="HyperInteractive",
        host="localhost",
        dbname="omnisci"
    )

    # Load a small sample from MySQL
    query = f"SELECT * FROM blazing_sql.{table_name}"
    if row_limit:
        query += f" LIMIT {row_limit}"

    print(f"📥 Loading data from MySQL table `{table_name}`...")
    df = pd.read_sql(query, con=engine)
    print(f"✅ Loaded {len(df)} rows.")

    # Convert all columns to string (TEXT-compatible)
    df = df.astype(str)

    print("🔍 Starting per-column import test...")

    for column in df.columns:
        print(f"\n🔎 Testing column: `{column}`")

        col_df = df[[column]].copy()

        # Drop and recreate the OmniSci test table with a single TEXT column
        try:
            omnisci.cursor().execute("DROP TABLE IF EXISTS debug_column_test;")
            omnisci.cursor().execute(f"CREATE TABLE debug_column_test ({column} TEXT);")
        except Exception as e:
            print(f"❌ Could not create table for `{column}`: {e}")
            continue

        # Attempt to import
        try:
            omnisci.load_table("debug_column_test", col_df)
            print(f"✅ Column `{column}` imported successfully.")
        except Exception as e:
            print(f"❌ Column `{column}` FAILED to import! Error: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_columns.py <table_name> [limit]")
        sys.exit(1)

    table = sys.argv[1]
    limit = int(sys.argv[2]) if len(sys.argv) == 3 else 100
    main(table, limit)
