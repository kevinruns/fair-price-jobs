import sqlite3
from werkzeug.security import generate_password_hash

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
    with sqlite3.connect('application.db') as conn:
        cursor = conn.cursor()  # Create a cursor object to execute SQL commands
        
        for user in dummy_users:
            hashed_password = generate_password_hash(user['password'])  # Hash the password
            
            # Prepare the SQL INSERT statement
            cursor.execute("""
                INSERT INTO users (username, firstname, lastname, email, postcode, hash) 
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user['username'], user['firstname'], user['lastname'], user['email'], user['postcode'], hashed_password))
        
        conn.commit()  # Commit the transaction
        print("Dummy users inserted!")



def load_db():
    with sqlite3.connect('application.db') as conn:
        with open(r'sql\load.sql', 'r') as f:
            sql_script = f.read()
            # print("SQL Script:")
            # print(sql_script)  # Add this line
            conn.executescript(sql_script)
    print("New database loaded.")



if __name__ == '__main__':
    add_users_to_db()
    load_db()



