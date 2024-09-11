import sqlite3

conn = sqlite3.connect('application.db')
cursor = conn.cursor()

# List all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables in the database:", tables)

# View data in a specific table
cursor.execute("SELECT * FROM tradesmen")
tradesmen = cursor.fetchall()
for tradesman in tradesmen:
    print(tradesman)

conn.close()