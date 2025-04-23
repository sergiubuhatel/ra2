import sys
import pandas as pd
from sqlalchemy import create_engine
from pyomnisci import connect


def main(table_name):
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

    print(f"Connecting to MySQL table `blazing_sql.{table_name}`...")
    try:
        df = pd.read_sql(f"SELECT * FROM blazing_sql.{table_name}", con=engine)
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

    # Drop existing table (optional but recommended for clean import)
    try:
        omnisci.execute(f"DROP TABLE IF EXISTS {table_name}")
        print(f"🗑️ Dropped existing table `{table_name}` in OmniSci.")
    except Exception as e:
        print(f"⚠️ Warning: could not drop existing table: {e}")

    # Load data into OmniSci
    try:
        print(f"⬆️ Loading data into OmniSci table `{table_name}`...")
        omnisci.load_table(table_name, df)
        print("✅ Import successful.")
    except Exception as e:
        print(f"❌ Error loading data into OmniSci: {e}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python mysql_to_omnisci.py <mysql_table_name>")
        sys.exit(1)

    table_name = sys.argv[1]
    main(table_name)
