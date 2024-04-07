import mysql.connector

# Establishing a connection to MySQL server
dataBase = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd=""
)

# Creating a cursor object
cursorObject = dataBase.cursor()

# Dropping the database if it exists
cursorObject.execute("DROP DATABASE IF EXISTS fetherstill_db")

# Committing the change
dataBase.commit()

# Closing the cursor and connection
cursorObject.close()
dataBase.close()
