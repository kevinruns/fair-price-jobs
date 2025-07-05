import sqlite3
import logging
from contextlib import contextmanager
from typing import Optional, List, Dict, Any, Tuple
from flask import g, current_app
from config import get_config

logger = logging.getLogger(__name__)

class DatabaseService:
    """Centralized database service for handling all database operations."""
    
    def __init__(self, database_path: Optional[str] = None):
        if database_path is None:
            config = get_config()
            database_path = config.DATABASE_PATH
        self.database_path = database_path
    
    def get_connection(self):
        if self.database_path is None:
            raise ValueError("Database path is not configured")
        try:
            # Try to use Flask's g object if we're in a Flask context
            if not hasattr(g, '_database'):
                g._database = sqlite3.connect(self.database_path, isolation_level=None)
                g._database.row_factory = sqlite3.Row
            return g._database
        except RuntimeError:
            # We're outside Flask context, create a direct connection
            if not hasattr(self, '_test_connection'):
                self._test_connection = sqlite3.connect(self.database_path, isolation_level=None)
                self._test_connection.row_factory = sqlite3.Row
            return self._test_connection
    
    def close_connection(self):
        """Close the database connection if it exists."""
        try:
            # Try to close Flask's g connection
            if hasattr(g, '_database'):
                g._database.close()
                delattr(g, '_database')
        except RuntimeError:
            # We're outside Flask context, close test connection
            if hasattr(self, '_test_connection'):
                self._test_connection.close()
                delattr(self, '_test_connection')
    
    @contextmanager
    def get_cursor(self):
        """Context manager for database cursor operations."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            yield cursor
        except Exception as e:
            logger.error(f"Database error: {e}")
            conn.rollback()
            raise
        finally:
            cursor.close()
    
    def execute_query(self, query: str, params: Tuple = ()) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return results as list of dictionaries."""
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            columns = [column[0] for column in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def execute_single_query(self, query: str, params: Tuple = ()) -> Optional[Dict[str, Any]]:
        """Execute a SELECT query and return a single result as dictionary."""
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            row = cursor.fetchone()
            if row:
                columns = [column[0] for column in cursor.description]
                return dict(zip(columns, row))
            return None
    
    def execute_insert(self, query: str, params: Tuple = ()) -> int:
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            lastrowid = cursor.lastrowid
            if lastrowid is None:
                return 0
            return int(lastrowid)

    def execute_update(self, query: str, params: Tuple = ()) -> int:
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            rowcount = cursor.rowcount
            if rowcount is None:
                return 0
            return int(rowcount)
    
    def execute_delete(self, query: str, params: Tuple = ()) -> int:
        """Execute a DELETE query and return the number of affected rows."""
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            rowcount = cursor.rowcount
            if rowcount is None:
                return 0
            return int(rowcount)
    
    def execute_transaction(self, queries: List[Tuple[str, Tuple]]) -> bool:
        """Execute multiple queries in a transaction."""
        conn = self.get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                for query, params in queries:
                    cursor.execute(query, params)
            return True
        except Exception as e:
            logger.error(f"Transaction error: {e}")
            return False
    
    def table_exists(self, table_name: str) -> bool:
        """Check if a table exists in the database."""
        query = """
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name=?
        """
        result = self.execute_single_query(query, (table_name,))
        return result is not None
    
    def get_table_info(self, table_name: str) -> List[Dict[str, Any]]:
        """Get information about table columns."""
        query = "PRAGMA table_info(?)"
        return self.execute_query(query, (table_name,))
    
    def init_db(self):
        """Initialize the database with the schema."""
        schema_sql = """
        DROP TABLE IF EXISTS users;
        DROP TABLE IF EXISTS groups;
        DROP TABLE IF EXISTS tradesmen;
        DROP TABLE IF EXISTS jobs;
        DROP TABLE IF EXISTS user_groups;
        DROP TABLE IF EXISTS group_tradesmen;
        DROP TABLE IF EXISTS user_tradesmen;

        -- users
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            firstname TEXT NOT NULL,
            lastname TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            postcode TEXT NOT NULL,
            hash TEXT NOT NULL
        );

        -- groups
        CREATE TABLE groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            postcode TEXT NOT NULL
        );

        -- Junction table for user-group relationship
        CREATE TABLE user_groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            group_id INTEGER,
            status TEXT NOT NULL CHECK(status IN ('creator', 'admin', 'member', 'pending')) DEFAULT 'pending',
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            FOREIGN KEY (group_id) REFERENCES groups (id) ON DELETE CASCADE
        );

        -- tradesmen
        CREATE TABLE tradesmen (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trade TEXT NOT NULL,
            first_name TEXT,
            family_name TEXT NOT NULL,
            company_name TEXT,
            address TEXT NOT NULL,
            postcode TEXT NOT NULL,
            phone_number TEXT NOT NULL,
            email TEXT
        );

        -- New junction table for group-tradesman relationship
        CREATE TABLE group_tradesmen (
            group_id INTEGER,
            tradesman_id INTEGER,
            PRIMARY KEY (group_id, tradesman_id),
            FOREIGN KEY (group_id) REFERENCES groups (id) ON DELETE CASCADE,
            FOREIGN KEY (tradesman_id) REFERENCES tradesmen (id) ON DELETE CASCADE
        );

        -- New junction table for user-tradesman relationship
        CREATE TABLE user_tradesmen (
            user_id INTEGER,
            tradesman_id INTEGER,
            date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (user_id, tradesman_id),
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            FOREIGN KEY (tradesman_id) REFERENCES tradesmen (id) ON DELETE CASCADE
        );

        -- New table for jobs and quotes
        CREATE TABLE jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            tradesman_id INTEGER NOT NULL,
            type TEXT NOT NULL CHECK (type IN ('job', 'quote')) DEFAULT 'job',
            date_started TEXT,
            date_finished TEXT,
            date_requested TEXT,
            date_received TEXT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            call_out_fee INTEGER NULL,
            materials_fee INTEGER NULL,
            hourly_rate INTEGER NULL,
            hours_worked REAL NULL,
            hours_estimated REAL NULL,
            daily_rate INTEGER NULL,
            days_worked REAL NULL,
            days_estimated REAL NULL,
            total_cost INTEGER NULL CHECK (total_cost IS NULL OR total_cost >= 0),
            total_quote INTEGER NULL CHECK (total_quote IS NULL OR total_quote >= 0),
            rating INTEGER NULL CHECK (rating IS NULL OR (rating >= 1 AND rating <= 5)),
            status TEXT CHECK (status IN ('pending', 'accepted', 'declined')) DEFAULT 'pending',
            FOREIGN KEY (tradesman_id) REFERENCES tradesmen (id) ON DELETE CASCADE
        );
        """
        
        # Execute the schema SQL
        conn = self.get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.executescript(schema_sql)
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

# Global database service instance
db_service = DatabaseService()

def get_db_service() -> DatabaseService:
    """Get the global database service instance."""
    return db_service 