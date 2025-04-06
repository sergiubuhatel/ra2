import pandas as pd
import pyomnisci
import argparse

# Function to quote column names to avoid conflicts
def quote_column_name(column_name):
    return f'"{column_name}"'

# Function to create the table in OmniSci (assumes columns are TEXT for simplicity)
def create_table_sql(df, table_name):
    create_table_sql = f"CREATE TABLE IF NOT EXISTS {table_name} (\n"
    for column in df.columns:
        quoted_column = quote_column_name(column)
        create_table_sql += f"    {quoted_column} TEXT,\n"  # All columns are TEXT
    create_table_sql = create_table_sql.rstrip(',\n') + "\n);"
    return create_table_sql

# Function to load data into OmniSci using batch inserts (optimized for performance)
def load_data_to_omnisci(csv_file, table_name, conn, batch_size=1000):
    bad_lines = 0
    good_lines = 0
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

    # Insert data into OmniSci using batch processing
    batch_values = []
    for index, row in df.iterrows():
        values = [f"'{str(value)}'" if value and len(value) > 0 else "''" for value in row]
        batch_values.append(f"({', '.join(values)})")

        # When batch size is reached, perform the insert
        if len(batch_values) >= batch_size:
            insert_sql = f"INSERT INTO {table_name} ({', '.join([quote_column_name(col) for col in df.columns])}) VALUES {', '.join(batch_values)};"
            try:
                conn.execute(insert_sql)
                conn.commit()
                batch_values.clear()  # Clear the batch for the next set
                good_lines += len(batch_values)
            except Exception as e:
                print(f"Error inserting batch: {e}")
                bad_lines += len(batch_values)

    # Insert any remaining rows in the final batch
    if batch_values:
        insert_sql = f"INSERT INTO {table_name} ({', '.join([quote_column_name(col) for col in df.columns])}) VALUES {', '.join(batch_values)};"
        try:
            conn.execute(insert_sql)
            conn.commit()
            good_lines += len(batch_values)
        except Exception as e:
            print(f"Error inserting final batch: {e}")
            bad_lines += len(batch_values)

    print(f"\nGood Lines: {good_lines}")
    print(f"\nBad Lines: {bad_lines}")

# Main function to handle command-line arguments
def main():
    parser = argparse.ArgumentParser(description="Load a CSV file into OmniSci")
    parser.add_argument('csv_file', type=str, help="Path to the CSV file")
    parser.add_argument('table_name', type=str, help="Name of the table in OmniSci")

    # Parse arguments
    args = parser.parse_args()

    # Connect to OmniSci
    conn = pyomnisci.connect(user='admin', password='HyperInteractive', host='localhost', port=6274)

    try:
        # Load data from CSV and insert into OmniSci table using batch inserts
        load_data_to_omnisci(args.csv_file, args.table_name, conn)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    main()
