import pytest
import tempfile
import os
from app.services.tradesman_service import TradesmanService
from app.services.database import DatabaseService
from main import create_app

class TestTradesmanDeletion:
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test database and services"""
        # Create a temporary file for the test database
        self.temp_db_fd, self.temp_db_path = tempfile.mkstemp(suffix='.db')
        os.close(self.temp_db_fd)  # Close the file descriptor
        
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['DATABASE'] = self.temp_db_path
        
        with self.app.app_context():
            self.db_service = DatabaseService(self.temp_db_path)
            self.db_service.init_db()
            self.tradesman_service = TradesmanService()
            
            # Create test users
            from app.services.user_service import UserService
            user_service = UserService()
            self.user1_id = user_service.create_user("testuser1", "Test", "User1", "test1@example.com", "12345", "password123")
            self.user2_id = user_service.create_user("testuser2", "Test", "User2", "test2@example.com", "12345", "password123")
            
            yield
        
        # Clean up the temporary database file
        try:
            os.unlink(self.temp_db_path)
        except OSError:
            pass  # File might already be deleted
    
    def test_can_user_delete_tradesman(self):
        """Test that users can only delete tradesmen they added"""
        # Create a tradesman for user1
        tradesman_id = self.tradesman_service.create_tradesman(
            "Plumber", "John", "Doe", "Doe Plumbing", "123 Main St", "12345", "555-1234", "john@example.com"
        )
        self.tradesman_service.add_user_tradesman_relationship(self.user1_id, tradesman_id)
        
        # User1 should be able to delete the tradesman
        assert self.tradesman_service.can_user_edit_tradesman(self.user1_id, tradesman_id) == True
        
        # User2 should not be able to delete the tradesman
        assert self.tradesman_service.can_user_edit_tradesman(self.user2_id, tradesman_id) == False
    
    def test_delete_tradesman_success(self):
        """Test successful deletion of a tradesman"""
        # Create a tradesman for user1
        tradesman_id = self.tradesman_service.create_tradesman(
            "Plumber", "John", "Doe", "Doe Plumbing", "123 Main St", "12345", "555-1234", "john@example.com"
        )
        self.tradesman_service.add_user_tradesman_relationship(self.user1_id, tradesman_id)
        
        # Verify tradesman exists
        tradesman = self.tradesman_service.get_tradesman_by_id(tradesman_id)
        assert tradesman is not None
        
        # Delete the tradesman
        result = self.tradesman_service.delete_tradesman(tradesman_id)
        assert result == True
        
        # Verify tradesman is deleted
        tradesman = self.tradesman_service.get_tradesman_by_id(tradesman_id)
        assert tradesman is None
    
    def test_delete_tradesman_with_jobs(self):
        """Test that deleting a tradesman also deletes associated jobs"""
        # Create a tradesman for user1
        tradesman_id = self.tradesman_service.create_tradesman(
            "Plumber", "John", "Doe", "Doe Plumbing", "123 Main St", "12345", "555-1234", "john@example.com"
        )
        self.tradesman_service.add_user_tradesman_relationship(self.user1_id, tradesman_id)
        
        # Add a job for the tradesman
        from app.services.job_service import JobService
        job_service = JobService()
        job_id = job_service.create_job(
            self.user1_id, tradesman_id, "job", "Test Job", "Test Description",
            total_cost=100
        )
        
        # Verify job exists
        job = job_service.get_job_by_id(job_id)
        assert job is not None
        
        # Delete the tradesman
        result = self.tradesman_service.delete_tradesman(tradesman_id)
        assert result == True
        
        # Verify job is also deleted (cascade deletion)
        job = job_service.get_job_by_id(job_id)
        assert job is None
    
    def test_delete_tradesman_with_group_associations(self):
        """Test that deleting a tradesman also removes group associations"""
        # Create a tradesman for user1
        tradesman_id = self.tradesman_service.create_tradesman(
            "Plumber", "John", "Doe", "Doe Plumbing", "123 Main St", "12345", "555-1234", "john@example.com"
        )
        self.tradesman_service.add_user_tradesman_relationship(self.user1_id, tradesman_id)
        
        # Create a group and add tradesman to it
        from app.services.group_service import GroupService
        group_service = GroupService()
        group_id = group_service.create_group("Test Group", "12345", "Test Description")
        group_service.add_user_to_group(self.user1_id, group_id, "creator")
        self.tradesman_service.add_tradesman_to_group(group_id, tradesman_id)
        
        # Verify tradesman is in group
        assert self.tradesman_service.is_tradesman_in_group(group_id, tradesman_id) == True
        
        # Delete the tradesman
        result = self.tradesman_service.delete_tradesman(tradesman_id)
        assert result == True
        
        # Verify tradesman is no longer in group (cascade deletion)
        assert self.tradesman_service.is_tradesman_in_group(group_id, tradesman_id) == False 