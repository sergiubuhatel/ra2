import pyomnisci

# Establish connection to OmniSciDB (Modify parameters as necessary)
conn = pyomnisci.connect(user='admin', password='HyperInteractive', host='localhost', port=6274)

# Create a cursor object to interact with the database
cursor = conn.cursor()

# SQL query to create a table
create_table_query = """
CREATE TABLE IF NOT EXISTS employees (
    id INT PRIMARY KEY,
    name TEXT,
    age INT,
    department TEXT
);
"""

# Execute the create table query
cursor.execute(create_table_query)

# Commit the transaction (if required)
conn.commit()

# Print success message
print("Table 'employees' created successfully!")

# Close the cursor and connection when done
cursor.close()
conn.close()
