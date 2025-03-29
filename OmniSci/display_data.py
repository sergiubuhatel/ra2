import pyomnisci

# Establish connection to OmniSciDB
conn = pyomnisci.connect(user='admin', password='HyperInteractive', host='localhost', port=6274)

# Create a new cursor object to query data
cursor = conn.cursor()

# SQL query to select all data from the 'employees' table
select_query = "SELECT * FROM employees;"

# Execute the select query
cursor.execute(select_query)

# Fetch and display results
results = cursor.fetchall()
print("Displaying Data from 'employees' table:")
for row in results:
    print(row)

# Close the cursor and connection
cursor.close()
conn.close()
