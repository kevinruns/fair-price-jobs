import sqlite3
import os

def init_db():
    """Initialize the database with the schema"""
    # Get the correct paths
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'application.db')
    schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
    
    print(f"Initializing database at: {db_path}")
    print(f"Using schema from: {schema_path}")
    
    try:
        with sqlite3.connect(db_path) as conn:
            with open(schema_path, 'r') as f:
                sql_script = f.read()
                conn.executescript(sql_script)
        print("Database initialized successfully.")
        
                
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise

if __name__ == '__main__':
    init_db()
