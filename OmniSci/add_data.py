import pyomnisci

# Establish connection to OmniSciDB
conn = pyomnisci.connect(user='admin', password='HyperInteractive', host='localhost', port=6274)

# Create a cursor object to interact with the database
cursor = conn.cursor()

# Step 1: Insert data into the 'employees' table one by one using dictionaries
insert_query = "INSERT INTO employees (id, name, age, department) VALUES (:id, :name, :age, :department);"

# Data to insert
data = [
    {'id': 1, 'name': 'Alice', 'age': 30, 'department': 'Engineering'},
    {'id': 2, 'name': 'Bob', 'age': 25, 'department': 'Marketing'},
    {'id': 3, 'name': 'Charlie', 'age': 35, 'department': 'Sales'},
    {'id': 4, 'name': 'David', 'age': 28, 'department': 'HR'}
]

# Insert each row
for row in data:
    cursor.execute(insert_query, row)

# Commit the transaction
conn.commit()

conn.close()
