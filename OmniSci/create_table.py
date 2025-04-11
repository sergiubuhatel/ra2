import pandas as pd
import pyomnisci
import argparse


# Function to quote column names to avoid conflicts
def quote_column_name(column_name):
    return f'"{column_name}"'  # OmniSci requires column names to be quoted


# Function to create the table in OmniSci
def create_table_sql(df, table_name):
    create_table_sql = f"CREATE TABLE IF NOT EXISTS {table_name} (\n"

    # Use TEXT for all columns, no type checking
    for column in df.columns:
        quoted_column = quote_column_name(column)
        create_table_sql += f"    {quoted_column} TEXT,\n"  # All columns are TEXT

    create_table_sql = create_table_sql.rstrip(',\n') + "\n);"
    return create_table_sql

# Function to load the data into OmniSci using raw SQL inserts
def create_table_sql_main(csv_file, table_name, conn):
    bad_lines = 0
    good_lines = 0
    # Load the CSV file into a pandas DataFrame
    try:
        df = pd.read_csv(csv_file, quotechar='"', on_bad_lines='skip')
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return

    # Replace NaN values with empty strings and convert all values to string
    df = df.fillna('').astype(str)

    # Create the table SQL query based on the DataFrame schema
    create_sql = create_table_sql(df, table_name)

    # Execute the SQL to create the table
    conn.execute(create_sql)
    conn.commit()

# Main function to handle command-line arguments
def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Load a CSV file into OmniSci")
    parser.add_argument('csv_file', type=str, help="Path to the CSV file")
    parser.add_argument('table_name', type=str, help="Name of the table in OmniSci")

    # Parse arguments
    args = parser.parse_args()

    # Connect to OmniSci
    conn = pyomnisci.connect(user='admin', password='HyperInteractive', host='localhost', port=6274)

    try:
        # Load data from CSV and insert into the OmniSci table
        create_table_sql_main(args.csv_file, args.table_name, conn)
        print(f"Created table '{args.table_name}'.")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        conn.commit()
        # Close the connection
        conn.close()


if __name__ == '__main__':
    main()
