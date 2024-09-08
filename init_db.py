import sqlite3

def init_db():
    with sqlite3.connect('application.db') as conn:
        with open('schema.sql', 'r') as f:
            sql_script = f.read()
            # print("SQL Script:")
            # print(sql_script)  # Add this line
            conn.executescript(sql_script)
    print("Database initialized successfully.")

if __name__ == '__main__':
    init_db()
