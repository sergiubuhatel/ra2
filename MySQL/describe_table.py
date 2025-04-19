import pandas as pd
import sqlalchemy
import argparse
import re

# MySQL ➡️ OmniSci type mapping
def mysql_to_omnisci(mysql_type):
    mysql_type = mysql_type.lower()
    if "int" in mysql_type:
        return "INTEGER"
    if "bigint" in mysql_type:
        return "BIGINT"
    if "float" in mysql_type:
        return "FLOAT"
    if "double" in mysql_type or "decimal" in mysql_type:
        return "DOUBLE"
    if "char" in mysql_type or "text" in mysql_type:
        return "TEXT"
    if "date" in mysql_type and "time" not in mysql_type:
        return "DATE"
    if "timestamp" in mysql_type or "datetime" in mysql_type:
        return "TIMESTAMP"
    if "boolean" in mysql_type or "tinyint(1)" in mysql_type:
        return "BOOLEAN"
    return "TEXT"  # fallback

# Parse command-line args
parser = argparse.ArgumentParser(description="Generate OmniSci CREATE TABLE statement from a MySQL table")
parser.add_argument("table_name", help="MySQL table name")
args = parser.parse_args()

# Connect to MySQL
engine = sqlalchemy.create_engine("mysql+pymysql://root:root@localhost/blazing_sql")

# Get column info
query = f"DESCRIBE {args.table_name}"
df = pd.read_sql(query, engine)

# Generate CREATE TABLE
print(f"CREATE TABLE {args.table_name} (")
column_defs = []
for _, row in df.iterrows():
    col = row["Field"]
    mysql_type = row["Type"]
    omnisci_type = mysql_to_omnisci(mysql_type)
    column_defs.append(f"    {col} {omnisci_type}")
print(",\n".join(column_defs))
print(");")
