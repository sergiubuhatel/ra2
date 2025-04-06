import pandas as pd
import pyomnisci
import argparse
import os

# Function to quote column names to avoid conflicts
def quote_column_name(column_name):
    return f'"{column_name}"'  # OmniSci requires column names to be quoted

# Function to create the table in OmniSci (assumes columns are TEXT for simplicity)
def create_table_sql(df, table_name):
    create_table_sql = f"CREATE TABLE IF NOT EXISTS {table_name} (\n"

    # Use TEXT for all columns, no type checking
    for column in df.columns:
        quoted_column = quote_column_name(column)
        create_table_sql += f"    {quoted_column} TEXT,\n"  # All columns are TEXT

    create_table_sql = create_table_sql.rstrip(',\n') + "\n);"
    return create_table_sql

# Function to load data into OmniSci using COPY (GPU optimized)
def load_data_to_omnisci(csv_file, table_name, conn):
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

    # Save the DataFrame to a temporary file (OmniSci's COPY command requires file input)
    temp_file = "temp_data.csv"
    df.to_csv(temp_file, index=False, header=True)

    # Perform the COPY operation to load the data into OmniSci
    try:
        # This uses the COPY command, which is optimized for GPU acceleration in OmniSci
        copy_sql = f"""
            COPY {table_name} FROM '{os.path.abspath(temp_file)}' WITH (header, delimiter=',');
        """
        conn.execute(copy_sql)
        conn.commit()
        print(f"Data loaded successfully into table '{table_name}' using GPU-accelerated COPY.")
        os.remove(temp_file)  # Clean up the temporary file
    except Exception as e:
        print(f"Error loading data using COPY: {e}")
        os.remove(temp_file)

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
        # Load data from CSV and insert into the OmniSci table using GPU acceleration
        load_data_to_omnisci(args.csv_file, args.table_name, conn)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Close the connection
        conn.close()

if __name__ == '__main__':
    main()
