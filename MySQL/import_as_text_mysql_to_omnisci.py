import sys
import pandas as pd
from sqlalchemy import create_engine
from pyomnisci import connect


def create_omnisci_table(omnisci, table_name, columns):
    print(f"🛠️ Creating table `{table_name}` in OmniSci...")

    try:
        omnisci.cursor().execute(f"DROP TABLE IF EXISTS {table_name};")
        print(f"🗑️ Dropped existing table `{table_name}`.")
    except Exception as e:
        print(f"⚠️ Could not drop existing table `{table_name}`: {e}")

    # Build table schema with all columns as TEXT
    column_defs = ",\n".join([f"{col} TEXT" for col in columns])
    create_sql = f"CREATE TABLE {table_name} (\n{column_defs}\n);"

    try:
        omnisci.cursor().execute(create_sql)
        print(f"✅ Table `{table_name}` created successfully.")
    except Exception as e:
        print(f"❌ Failed to create table `{table_name}`: {e}")
        sys.exit(1)


def main(table_name, row_limit=None):
    # MySQL connection settings
    mysql_user = "root"
    mysql_pass = "root"
    mysql_host = "localhost"
    mysql_port = 3307
    mysql_db = "blazing_sql"

    # OmniSci settings
    omnisci_user = "admin"
    omnisci_pass = "HyperInteractive"
    omnisci_host = "localhost"
    omnisci_db = "omnisci"

    # Connect to MySQL
    mysql_url = f"mysql+pymysql://{mysql_user}:{mysql_pass}@{mysql_host}:{mysql_port}/{mysql_db}"
    engine = create_engine(mysql_url)

    query = f"SELECT * FROM {mysql_db}.{table_name}"
    if row_limit:
        query += f" LIMIT {row_limit}"

    print(f"📥 Loading data from MySQL table `{table_name}`...")
    try:
        df = pd.read_sql(query, con=engine)
        print(f"✅ Loaded {len(df)} rows.")
    except Exception as e:
        print(f"❌ Failed to load data from MySQL: {e}")
        sys.exit(1)

    # Convert all columns to string
    df = df.astype(str)

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
        print(f"❌ Could not connect to OmniSci: {e}")
        sys.exit(1)

    # Create table with all TEXT columns
    create_omnisci_table(omnisci, table_name, df.columns)

    # Convert to numpy string arrays to avoid ChunkedArray error
    df = df.apply(lambda col: col.astype(str).values)

    # Load into OmniSci
    try:
        print(f"⬆️ Loading data into OmniSci table `{table_name}`...")
        chunk_size = 1000000
        num_chunks = (len(df) + chunk_size - 1) // chunk_size

        for i in range(num_chunks):
            start = i * chunk_size
            end = min((i + 1) * chunk_size, len(df))
            print(f"📦 Loading rows {start} to {end}...")
            try:
                chunk = df.iloc[start:end]
                omnisci.load_table(table_name, chunk)
            except Exception as e:
                print(f"❌ Error loading chunk {i}: {e}")
                sys.exit(1)

        print("✅ Import successful.")
    except Exception as e:
        print(f"❌ Error loading data into OmniSci: {e}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python mysql_to_omnisci.py <mysql_table_name> [limit]")
        sys.exit(1)

    table = sys.argv[1]
    limit = int(sys.argv[2]) if len(sys.argv) == 3 else None
    main(table, limit)
