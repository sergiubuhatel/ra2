import time
import argparse
from blazingsql import BlazingContext
import cudf  # RAPIDS cuDF for GPU-accelerated dataframes

# Command-line argument parser
parser = argparse.ArgumentParser(description="Load a CSV file into BlazingSQL and query it.")
parser.add_argument("file", help="Path to the CSV file.")
parser.add_argument("table", help="Name of the table to create.")
args = parser.parse_args()

bc = BlazingContext()

start_time = time.time()
bc.create_table(args.table, args.file)
end_time = time.time()

print(f"Time taken to load the file: {end_time - start_time} seconds")

query = f"SELECT 'AFL' AS AFL, screen_name4, COUNT(*) AS numConnections" \
f" FROM {args.table}" \
f" WHERE screen_name4 <> 'AFL'" \
f" AND tweet_text LIKE '%AFL%'" \
f" GROUP BY screen_name4"


#query = f"SELECT \"AFL\", screen_name4, count(*) as numConnections FROM {args.table} " \
#        f"WHERE screen_name4!= 'AFL' AND tweet_text REGEXP '\\$\\bAFL\\$' group by screen_name4"
result = bc.sql(query)
print(result)