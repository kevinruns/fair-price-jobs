import sqlite3
import logging
from contextlib import contextmanager
from typing import Optional, List, Dict, Any, Tuple
from flask import g, current_app
from app.config import DATABASE

logger = logging.getLogger(__name__)

class DatabaseService:
    """Centralized database service for handling all database operations."""
    
    def __init__(self, database_path: str = DATABASE):
        self.database_path = database_path
    
    def get_connection(self) -> sqlite3.Connection:
        """Get a database connection, creating it if necessary."""
        if not hasattr(g, '_database'):
            g._database = sqlite3.connect(self.database_path, isolation_level=None)
            g._database.row_factory = sqlite3.Row
        return g._database
    
    def close_connection(self):
        """Close the database connection if it exists."""
        if hasattr(g, '_database'):
            g._database.close()
            delattr(g, '_database')
    
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
        """Execute an INSERT query and return the last row ID."""
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            return cursor.lastrowid
    
    def execute_update(self, query: str, params: Tuple = ()) -> int:
        """Execute an UPDATE query and return the number of affected rows."""
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            return cursor.rowcount
    
    def execute_delete(self, query: str, params: Tuple = ()) -> int:
        """Execute a DELETE query and return the number of affected rows."""
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            return cursor.rowcount
    
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

# Global database service instance
db_service = DatabaseService()

def get_db_service() -> DatabaseService:
    """Get the global database service instance."""
    return db_service 