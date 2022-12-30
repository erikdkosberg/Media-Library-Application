import os
import sqlite3

# Connect to the database
# Default directory stored into by the 'Photos' application
print(os.getcwd())
os.chdir("/Users/erikdkosberg/Pictures")

# Photos\Photo Library.photolibrary
path = os.listdir()[-1]
os.chdir(path)

# This is where the sqlite tables are
os.chdir("database")
conn = sqlite3.connect('Photos.sqlite')
cursor = conn.cursor()

# Execute a SELECT statement to retrieve all rows from the photos table
cursor.execute('SELECT * FROM ZASSET')

# Fetch all of the rows from the result set
rows = cursor.fetchall()

# Iterate through the rows and print the values for each column
for row in rows:
    print(row)

# Close the connection to the database
conn.close()
