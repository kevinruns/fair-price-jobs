import sqlite3
import sys
from pathlib import Path
from werkzeug.security import generate_password_hash

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import get_config

# Updated dummy user data
dummy_users = [
    {'username': 'johndoe', 'firstname': 'John', 'lastname': 'Doe', 'email': 'johndoe@example.com', 'postcode': '12345', 'password': 'pass'},
    {'username': 'janedoe', 'firstname': 'Jane', 'lastname': 'Doe', 'email': 'janedoe@example.com', 'postcode': '12345', 'password': 'pass'},
    {'username': 'alice', 'firstname': 'Alice', 'lastname': 'Smith', 'email': 'alice@example.com', 'postcode': '67890', 'password': 'pass'},
    {'username': 'bob', 'firstname': 'Bob', 'lastname': 'Johnson', 'email': 'bob@example.com', 'postcode': '67890', 'password': 'pass'},
    {'username': 'charlie', 'firstname': 'Charlie', 'lastname': 'Brown', 'email': 'charlie@example.com', 'postcode': '54321', 'password': 'pass'},
    {'username': 'david', 'firstname': 'David', 'lastname': 'Williams', 'email': 'david@example.com', 'postcode': '12345', 'password': 'pass'},
    {'username': 'emma', 'firstname': 'Emma', 'lastname': 'Jones', 'email': 'emma@example.com', 'postcode': '54321', 'password': 'pass'},
    {'username': 'frank', 'firstname': 'Frank', 'lastname': 'Garcia', 'email': 'frank@example.com', 'postcode': '67890', 'password': 'pass'},
    {'username': 'grace', 'firstname': 'Grace', 'lastname': 'Martinez', 'email': 'grace@example.com', 'postcode': '12345', 'password': 'pass'},
    {'username': 'henry', 'firstname': 'Henry', 'lastname': 'Lopez', 'email': 'henry@example.com', 'postcode': '67890', 'password': 'pass'},
]

def add_users_to_db():
    """Add dummy users to the database."""
    config = get_config()
    db_path = config.DATABASE_PATH
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        for user in dummy_users:
            hashed_password = generate_password_hash(user['password'])
            
            cursor.execute("""
                INSERT INTO users (username, firstname, lastname, email, postcode, hash) 
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user['username'], user['firstname'], user['lastname'], user['email'], user['postcode'], hashed_password))
        
        conn.commit()
        print("Dummy users inserted!")

def load_db():
    """Load sample data into the database."""
    config = get_config()
    db_path = config.DATABASE_PATH
    load_sql_path = Path(__file__).parent / 'load.sql'
    
    with sqlite3.connect(db_path) as conn:
        with open(load_sql_path, 'r') as f:
            sql_script = f.read()
            conn.executescript(sql_script)
    print("Sample data loaded successfully.")

if __name__ == '__main__':
    load_db()



