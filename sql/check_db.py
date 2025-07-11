#!/usr/bin/env python3

import sqlite3
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import get_config

def check_database():
    """Check what's in the database"""
    
    # Get configuration
    config = get_config()
    db_path = config.DATABASE_PATH
    
    if not Path(db_path).exists():
        print(f"Database file not found: {db_path}")
        return
    
    print(f"Checking database: {db_path}")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # List all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"Tables in database: {[table[0] for table in tables]}")
        print()
        
        # Check each table
        for table in tables:
            table_name = table[0]
            print(f"Table: {table_name}")
            print("-" * 30)
            
            # Get table schema
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            print("Columns:")
            for col in columns:
                print(f"  {col[1]} ({col[2]})")
            print()
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"Row count: {count}")
            
            # Show first few rows if any exist
            if count > 0:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
                rows = cursor.fetchall()
                print("First few rows:")
                for i, row in enumerate(rows, 1):
                    print(f"  Row {i}: {row}")
            else:
                print("  (No data)")
            print()
        
        conn.close()
        
    except Exception as e:
        print(f"Error checking database: {e}")

if __name__ == "__main__":
    check_database() 