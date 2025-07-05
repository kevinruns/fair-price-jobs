import sqlite3
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import get_config

def read_database():
    """Read and display database contents."""
    config = get_config()
    db_path = config.DATABASE_PATH
    
    conn = sqlite3.connect(db_path)
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

if __name__ == '__main__':
    read_database()