import pyomnisci

# Connect to OmniSciDB (modify the parameters based on your setup)
conn = pyomnisci.connect(user='admin', password='HyperInteractive', host='localhost', port=6274)

# Create a cursor object
cursor = conn.cursor()

# Run the SQL query to fetch all table names in the 'omnisci' schema
cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'omnisci'")

# Fetch and print results
tables = cursor.fetchall()

for table in tables:
    print(table[0])

# Close the cursor and connection
cursor.close()
conn.close()
