from typing import Optional, Dict, Any
from werkzeug.security import check_password_hash, generate_password_hash
from app.services.database import get_db_service
from app.exceptions import NotFoundError, DuplicateResourceError, AuthenticationError, ValidationError

class UserService:
    """Service class for user-related database operations."""
    
    def __init__(self):
        self.db = get_db_service()
    
    def create_user(self, username: str, firstname: str, lastname: str, 
                   email: str, postcode: str, password: str) -> int:
        """Create a new user."""
        # Validate input
        if not all([username, firstname, lastname, email, postcode, password]):
            raise ValidationError("All fields are required")
        
        if len(password) < 6:
            raise ValidationError("Password must be at least 6 characters long")
        
        # Check if user already exists
        existing_user = self.get_user_by_username(username)
        if existing_user:
            raise DuplicateResourceError("Username already taken")
        
        existing_email = self.get_user_by_email(email)
        if existing_email:
            raise DuplicateResourceError("Email already registered")
        
        # Hash password
        hashed_password = generate_password_hash(password)
        
        # Insert user
        try:
            user_id = self.db.execute_insert(
                "INSERT INTO users (username, firstname, lastname, email, postcode, hash) VALUES (?, ?, ?, ?, ?, ?)",
                (username, firstname, lastname, email, postcode, hashed_password)
            )
            return user_id
        except Exception as e:
            raise DuplicateResourceError("Failed to create user. Username or email may already exist.")
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID."""
        return self.db.execute_single_query(
            "SELECT * FROM users WHERE id = ?",
            (user_id,)
        )
    
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username."""
        return self.db.execute_single_query(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        )
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email."""
        return self.db.execute_single_query(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        )
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user with username and password."""
        user = self.get_user_by_username(username)
        
        if user and check_password_hash(user['hash'], password):
            return user
        
        return None
    
    def update_user(self, user_id: int, **kwargs) -> bool:
        """Update user information."""
        # Validate user exists
        user = self.get_user_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")
        
        # Build update query
        allowed_fields = ['firstname', 'lastname', 'email', 'postcode']
        update_fields = []
        params = []
        
        for field, value in kwargs.items():
            if field in allowed_fields and value is not None:
                update_fields.append(f"{field} = ?")
                params.append(value)
        
        if not update_fields:
            raise ValidationError("No valid fields to update")
        
        # Add user_id to params
        params.append(user_id)
        
        # Execute update
        query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = ?"
        affected_rows = self.db.execute_update(query, tuple(params))
        
        return affected_rows > 0
    
    def get_all_users(self) -> list:
        """Get all users."""
        return self.db.execute_query(
            "SELECT id, username, firstname, lastname, email, postcode FROM users ORDER BY username"
        )
    
    def delete_user(self, user_id: int) -> bool:
        """Delete a user."""
        # Validate user exists
        user = self.get_user_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")
        
        # Delete user
        affected_rows = self.db.execute_delete(
            "DELETE FROM users WHERE id = ?",
            (user_id,)
        )
        
        return affected_rows > 0
    
    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """Get user statistics."""
        # Validate user exists
        user = self.get_user_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")
        
        # Get tradesmen count
        tradesmen_result = self.db.execute_single_query(
            "SELECT COUNT(*) as count FROM user_tradesmen WHERE user_id = ?",
            (user_id,)
        )
        tradesmen_count = tradesmen_result['count'] if tradesmen_result else 0
        
        # Get groups count
        groups_result = self.db.execute_single_query(
            "SELECT COUNT(*) as count FROM user_groups WHERE user_id = ? AND status != 'pending'",
            (user_id,)
        )
        groups_count = groups_result['count'] if groups_result else 0
        
        # Get jobs count
        jobs_result = self.db.execute_single_query(
            "SELECT COUNT(*) as count FROM jobs WHERE user_id = ?",
            (user_id,)
        )
        jobs_count = jobs_result['count'] if jobs_result else 0
        
        return {
            'tradesmen_count': tradesmen_count,
            'groups_count': groups_count,
            'jobs_count': jobs_count
        } 