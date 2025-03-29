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

print("Data inserted successfully!")

# Step 2: Select and display data from the 'employees' table
select_query = "SELECT * FROM employees;"

cursor.execute(select_query)
results = cursor.fetchall()

# Display the data
print("Displaying Data from 'employees' table:")
for row in results:
    print(row)

# Close the cursor and connection
cursor.close()
conn.close()
