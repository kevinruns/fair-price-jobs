import sqlite3
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import get_config

def init_db():
    """Initialize the database with the schema"""
    # Get configuration
    config = get_config()
    
    # Get the database path
    db_path = config.DATABASE_PATH
    schema_path = Path(__file__).parent / 'schema.sql'
    
    print(f"Initializing database at: {db_path}")
    print(f"Using schema from: {schema_path}")
    
    try:
        # Ensure database directory exists
        db_dir = Path(db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
        
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
