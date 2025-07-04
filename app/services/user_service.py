from typing import Optional, List, Dict, Any
from werkzeug.security import generate_password_hash, check_password_hash
from app.services.database import get_db_service

class UserService:
    """Service class for user-related database operations."""
    
    def __init__(self):
        self.db = get_db_service()
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID."""
        query = "SELECT * FROM users WHERE id = ?"
        return self.db.execute_single_query(query, (user_id,))
    
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username."""
        query = "SELECT * FROM users WHERE username = ?"
        return self.db.execute_single_query(query, (username,))
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email."""
        query = "SELECT * FROM users WHERE email = ?"
        return self.db.execute_single_query(query, (email,))
    
    def create_user(self, username: str, firstname: str, lastname: str, 
                   email: str, postcode: str, password: str) -> int:
        """Create a new user and return the user ID."""
        hashed_password = generate_password_hash(password)
        query = """
            INSERT INTO users (username, firstname, lastname, email, postcode, hash)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        return self.db.execute_insert(query, (username, firstname, lastname, email, postcode, hashed_password))
    
    def update_user(self, user_id: int, **kwargs) -> bool:
        """Update user information."""
        allowed_fields = ['firstname', 'lastname', 'email', 'postcode']
        update_fields = []
        params = []
        
        for field, value in kwargs.items():
            if field in allowed_fields and value is not None:
                update_fields.append(f"{field} = ?")
                params.append(value)
        
        if not update_fields:
            return False
        
        params.append(user_id)
        query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = ?"
        return self.db.execute_update(query, tuple(params)) > 0
    
    def change_password(self, user_id: int, new_password: str) -> bool:
        """Change user password."""
        hashed_password = generate_password_hash(new_password)
        query = "UPDATE users SET hash = ? WHERE id = ?"
        return self.db.execute_update(query, (hashed_password, user_id)) > 0
    
    def verify_password(self, username: str, password: str) -> bool:
        """Verify username and password combination."""
        query = "SELECT hash FROM users WHERE username = ?"
        result = self.db.execute_single_query(query, (username,))
        if result:
            return check_password_hash(result['hash'], password)
        return False
    
    def get_user_groups(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all groups that a user belongs to."""
        query = """
            SELECT g.*, ug.status, 
                   (SELECT COUNT(*) FROM user_groups WHERE group_id = g.id) as member_count
            FROM groups g
            JOIN user_groups ug ON g.id = ug.group_id
            WHERE ug.user_id = ?
            ORDER BY g.name
        """
        return self.db.execute_query(query, (user_id,))
    
    def get_user_tradesmen(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all tradesmen associated with a user."""
        query = """
            SELECT t.*, 
                   COUNT(j.id) as job_count,
                   AVG(j.rating) as avg_rating,
                   ut.date_added
            FROM tradesmen t
            JOIN user_tradesmen ut ON t.id = ut.tradesman_id
            LEFT JOIN jobs j ON t.id = j.tradesman_id
            WHERE ut.user_id = ?
            GROUP BY t.id
            ORDER BY t.trade, t.family_name, t.first_name, t.company_name
        """
        return self.db.execute_query(query, (user_id,))
    
    def get_user_jobs(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all jobs created by a user."""
        query = """
            SELECT j.*, t.first_name, t.family_name, t.trade
            FROM jobs j
            JOIN tradesmen t ON j.tradesman_id = t.id
            WHERE j.user_id = ?
            ORDER BY j.date_started DESC
        """
        return self.db.execute_query(query, (user_id,))
    
    def delete_user(self, user_id: int) -> bool:
        """Delete a user and all associated data."""
        # This would need to be implemented with proper cascade handling
        # For now, just return False to prevent accidental deletions
        return False 