import pytest
from app.services.group_service import GroupService
from app.services.database import DatabaseService
import tempfile
import os

class TestDuplicateRequests:
    """Test that duplicate join requests are prevented."""
    
    def setup_method(self):
        """Set up test database."""
        # Create a temporary database file
        self.db_fd, self.db_path = tempfile.mkstemp()
        
        # Initialize database with schema
        db_service = DatabaseService(self.db_path)
        db_service.init_db()
        
        self.group_service = GroupService()
        # Override the database path for the service
        self.group_service.db = db_service
    
    def teardown_method(self):
        """Clean up test database."""
        # Close the database connection first
        if hasattr(self.group_service, 'db'):
            self.group_service.db.close_connection()
        os.close(self.db_fd)
        os.unlink(self.db_path)
    
    def test_duplicate_join_requests_prevented(self):
        """Test that a user cannot create multiple join requests for the same group."""
        # Create a test user and group
        user_id = 1
        group_id = 1
        
        # Insert test user and group directly
        self.group_service.db.execute_insert(
            "INSERT INTO users (id, username, firstname, lastname, email, postcode, hash) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (user_id, "testuser", "Test", "User", "test@example.com", "12345", "hash")
        )
        self.group_service.db.execute_insert(
            "INSERT INTO groups (id, name, postcode) VALUES (?, ?, ?)",
            (group_id, "Test Group", "12345")
        )
        
        # First request should succeed
        result1 = self.group_service.add_user_to_group(user_id, group_id, 'pending')
        assert result1 is True
        
        # Second request should fail (return False due to unique constraint)
        result2 = self.group_service.add_user_to_group(user_id, group_id, 'pending')
        assert result2 is False
        
        # Verify only one record exists
        records = self.group_service.db.execute_query(
            "SELECT * FROM user_groups WHERE user_id = ? AND group_id = ?",
            (user_id, group_id)
        )
        assert len(records) == 1
        assert records[0]['status'] == 'pending'
    
    def test_different_statuses_allowed(self):
        """Test that a user can have different statuses for the same group (e.g., pending -> member)."""
        # Create a test user and group
        user_id = 1
        group_id = 1
        
        # Insert test user and group directly
        self.group_service.db.execute_insert(
            "INSERT INTO users (id, username, firstname, lastname, email, postcode, hash) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (user_id, "testuser", "Test", "User", "test@example.com", "12345", "hash")
        )
        self.group_service.db.execute_insert(
            "INSERT INTO groups (id, name, postcode) VALUES (?, ?, ?)",
            (group_id, "Test Group", "12345")
        )
        
        # Add user as pending
        result1 = self.group_service.add_user_to_group(user_id, group_id, 'pending')
        assert result1 is True
        
        # Update status to member (should work)
        result2 = self.group_service.update_user_group_status(user_id, group_id, 'member')
        assert result2 is True
        
        # Verify the status was updated
        membership = self.group_service.get_user_group_membership(user_id, group_id)
        assert membership['status'] == 'member' 