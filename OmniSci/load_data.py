import pandas as pd
import pyomnisci
import argparse


# Function to determine OmniSci data type based on Pandas dtype
def pandas_to_omniscidb_dtype(pandas_dtype):
    if pandas_dtype == 'int64':
        return 'INT'
    elif pandas_dtype == 'float64':
        return 'FLOAT'
    elif pandas_dtype == 'object':
        return 'TEXT'
    elif pandas_dtype == 'bool':
        return 'BOOLEAN'
    else:
        return 'TEXT'  # Default to TEXT if unrecognized type


# Function to quote column names to avoid conflicts
def quote_column_name(column_name):
    return f'"{column_name}"'  # OmniSci requires column names to be quoted


# Function to create the table in OmniSci
def create_table_sql(df, table_name):
    create_table_sql = f"CREATE TABLE IF NOT EXISTS {table_name} (\n"

    for column, dtype in df.dtypes.items():
        # Quote the column name to avoid any conflicts
        quoted_column = quote_column_name(column)
        omnisci_type = pandas_to_omniscidb_dtype(dtype)
        create_table_sql += f"    {quoted_column} {omnisci_type},\n"

    # Remove the last comma and newline, then close the parentheses
    create_table_sql = create_table_sql.rstrip(',\n') + "\n);"

    return create_table_sql


# Function to load the data into OmniSci using raw SQL inserts
def load_data_to_omnisci(csv_file, table_name, conn):
    # Load the CSV file into a pandas DataFrame, skipping bad lines
    try:
        df = pd.read_csv(csv_file, on_bad_lines='skip', quotechar='"')
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return

    # Convert quoted strings that represent integers to actual integers
    for column in df.columns:
        # If column dtype is object (string), try to convert to int
        if df[column].dtype == 'object':
            try:
                # Try converting the column to integers
                df[column] = pd.to_numeric(df[column], errors='raise')
            except ValueError:
                pass  # If conversion fails, leave the column as object (string)

    # Create the table SQL query based on the DataFrame schema
    create_sql = create_table_sql(df, table_name)

    # Execute the SQL to create the table
    conn.execute(create_sql)

    # Insert data into OmniSci using raw SQL INSERT INTO
    for _, row in df.iterrows():
        # Prepare the row data for insertion (quote string values)
        values = [f"'{str(value)}'" if isinstance(value, str) else str(value) for value in row]

        # Quote the column names in the INSERT statement
        quoted_columns = [quote_column_name(col) for col in df.columns]
        insert_sql = f"INSERT INTO {table_name} ({', '.join(quoted_columns)}) VALUES ({', '.join(values)});"

        try:
            conn.execute(insert_sql)
        except Exception as e:
            print(f"Error inserting row: {row}\n{e}")


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
        load_data_to_omnisci(args.csv_file, args.table_name, conn)
        print(f"Data loaded successfully into table '{args.table_name}'.")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Close the connection
        conn.close()


if __name__ == '__main__':
    main()
