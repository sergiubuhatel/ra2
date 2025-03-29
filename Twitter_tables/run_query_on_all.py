import time
import os
import argparse
from blazingsql import BlazingContext
import cudf  # RAPIDS cuDF for GPU-accelerated dataframes

def list_files(directory):
    # Get all the files in the directory
    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    return files

def remove_substring(original_string, substring):
    # Replace the substring with an empty string and return a new string
    return original_string.replace(substring, "")

tables = []
bc = BlazingContext()

def import_directory(bc, directory, exclude_files):
    files = list_files(directory)

    for file in files:
        if file in exclude_files:
            print(f"\n\nFile {file} has been excluded\n\n")
            continue
        start_time = time.time()
        table = remove_substring(file, ".csv")
        tables.append(table)
        print(f"\nImporting file {directory}/{file} into table {table}...")
        bc.create_table(table, directory + "/" + file)
        end_time = time.time()
        print(f"Done. It took: {end_time - start_time} seconds\n")

        query = f"SELECT 'AFL' AS AFL, screen_name4, COUNT(*) AS numConnections" \
                f" FROM {table}" \
                f" WHERE screen_name4 <> 'AFL'" \
                f" AND tweet_text LIKE '%AFL%'" \
                f" GROUP BY screen_name4"


        #query = f"SELECT \"AFL\", screen_name4, count(*) as numConnections FROM {args.table} " \
        #        f"WHERE screen_name4!= 'AFL' AND tweet_text REGEXP '\\$\\bAFL\\$' group by screen_name4"
        print(f"\nQuerying table {table}...")
        start_time = time.time()
        result = bc.sql(query)
        end_time = time.time()
        print(f"Done. It took: {end_time - start_time} seconds\n")
        print(result)

def generate_union_sql(tables):
    global sql_statement
    first = True
    for table in tables:
        if first:
            sql_statement = f""
            first = False
        else:
            sql_statement = sql_statement + f" UNION "
        sql_statement = sql_statement + f" SELECT * FROM {table} "

    sql_statement = sql_statement + " LIMIT 5"
    return sql_statement

def query_union(tables):
    query = generate_union_sql(tables)
    print(f"\nQuerying union: {query}...")
    start_time = time.time()
    result = bc.sql(query)
    end_time = time.time()
    print(f"Done. It took: {end_time - start_time} seconds\n")
    print(result)

# directories = ['Twitter_2017', 'Twitter_2018', 'Twitter_2019', 'Twitter_2020', 'Twitter_2021',
#                'Twitter_2022', 'Twitter_2023']
directories = ['Twitter_2017']
exclude_files = ['chunk_10_fixed_Twitter_2022.csv']

for directory in directories:
    import_directory(bc, directory, exclude_files)

query_union(tables)

