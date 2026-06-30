import sqlite3
## connect to sqlite

connection = sqlite3.connect('student.db')

# Create a cursor object to insert record, create table
cursor = connection.cursor()

## create the table
table_info = """
CREATE TABLE IF NOT EXISTS students (
    Name VARCHAR(25),
    Class VARCHAR(25),
    Age INTEGER
);
"""

cursor.execute(table_info)

## insert record into the table
cursor.execute("""INSERT INTO students (Name, Class, Age) VALUES ('John Doe', 'A', 20);""")
cursor.execute("""INSERT INTO students (Name, Class, Age) VALUES ('Jane Smith', 'B', 22);""")
cursor.execute("""INSERT INTO students (Name, Class, Age) VALUES ('Pedro', 'B', 34);""")
cursor.execute("""INSERT INTO students (Name, Class, Age) VALUES ('Fulano', 'C', 24);""")
cursor.execute("""INSERT INTO students (Name, Class, Age) VALUES ('Matheus', 'D', 28);""")

## Display the records
data = cursor.execute("""SELECT * FROM students;""")
for row in data:
    print(row)

## commit the changes to the database
connection.commit()
connection.close()
