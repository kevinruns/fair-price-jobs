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
                g._database.execute("PRAGMA foreign_keys = ON")
            return g._database
        except RuntimeError:
            # We're outside Flask context, create a direct connection
            if not hasattr(self, '_test_connection'):
                self._test_connection = sqlite3.connect(self.database_path, isolation_level=None)
                self._test_connection.row_factory = sqlite3.Row
                self._test_connection.execute("PRAGMA foreign_keys = ON")
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
        """Initialize the database with the schema from sql/schema.sql."""
        schema_path = 'sql/schema.sql'
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        conn = self.get_connection()
        with conn:
            conn.executescript(schema_sql)

# Global database service instance
db_service = DatabaseService()

def get_db_service() -> DatabaseService:
    """Get the global database service instance."""
    return db_service 