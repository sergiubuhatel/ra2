import time
from blazingsql import BlazingContext
import cudf  # RAPIDS cuDF for GPU-accelerated dataframes

bc = BlazingContext()

start_time = time.time()
bc.create_table('Twitter_2017_table', '/mnt/data/twitter_tables/Twitter_2017.csv')
end_time = time.time()

print(f"Time taken to load the file: {end_time - start_time} seconds")

result = bc.sql("SELECT * FROM Twitter_2017_table LIMIT 5")
print(result)

