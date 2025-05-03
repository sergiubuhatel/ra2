import sys
import pandas as pd
import time
from pyomnisci import connect

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

    # Create the new destination table with coordinates as INTEGER
    create_sql = f"""
    CREATE TABLE {table_name} (
        coordinates INTEGER
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

    try:
        omnisci.load_table(table_name, df)
        print("✅ Data inserted successfully.")
    except Exception as e:
        print(f"❌ Error inserting data into OmniSci: {e}")
        sys.exit(1)

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
        print("✅ Connected to OmniSci.")
    except Exception as e:
        print(f"❌ Could not connect to OmniSci: {e}")
        sys.exit(1)

    # Prepare the query for source table
    query = f"SELECT * FROM {source_table}"
    if row_limit:
        query += f" LIMIT {row_limit}"

    print(f"📥 Fetching data from `{source_table}`... with query `{query}`")
    try:
        df = fetch_table_as_dataframe(omnisci, query)
        print(f"✅ Loaded {len(df)} rows, {len(df.columns)} columns.")
        
        # Print the first few rows of the dataframe for inspection
        print("\nFirst few rows of the data fetched:")
        print(df.head())  # Display first 5 rows of the dataframe

    except Exception as e:
        print(f"❌ Failed to load data from OmniSci: {e}")
        sys.exit(1)

    # Create destination table with a single `coordinates` column as INTEGER
    create_destination_table(omnisci, target_table)

    # Ensure `coordinates` is of type int32 before inserting
    if 'coordinates' in df.columns:
        # Convert `coordinates` to int32 (handle any NaN values by filling them with 0)
        df_to_insert = df[['coordinates']].copy()
        df_to_insert['coordinates'] = pd.to_numeric(df_to_insert['coordinates'], errors='coerce').fillna(0).astype('int32')
    else:
        print("❌ Coordinates column not found in source data.")
        sys.exit(1)

    # Insert data into the destination table
    insert_data_into_table(omnisci, target_table, df_to_insert)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python test_column_imports.py <source_table> <destination_table> [limit]")
        sys.exit(1)

    source_table = sys.argv[1]
    target_table = sys.argv[2]
    limit = int(sys.argv[3]) if len(sys.argv) == 4 else None

    main(source_table, target_table, limit)
