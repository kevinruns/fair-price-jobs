import pytest
import tempfile
import os
from app.services.job_service import JobService
from app.services.tradesman_service import TradesmanService
from app.services.database import DatabaseService
from main import create_app

class TestJobDeletion:
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
            self.job_service = JobService()
            self.tradesman_service = TradesmanService()
            
            # Create test users
            from app.services.user_service import UserService
            user_service = UserService()
            self.user1_id = user_service.create_user("testuser1", "Test", "User1", "test1@example.com", "12345", "password123")
            self.user2_id = user_service.create_user("testuser2", "Test", "User2", "test2@example.com", "12345", "password123")
            
            # Create a test tradesman
            tradesman_id = self.tradesman_service.create_tradesman(
                "Plumber", "John", "Doe", "Doe Plumbing", "123 Main St", "12345", "555-1234", "john@example.com"
            )
            self.tradesman_service.add_user_tradesman_relationship(self.user1_id, tradesman_id)
            self.tradesman_id = tradesman_id
            
            yield
        
        # Clean up the temporary database file
        try:
            os.unlink(self.temp_db_path)
        except OSError:
            pass  # File might already be deleted
    
    def test_can_user_delete_job(self):
        """Test that users can only delete jobs they created"""
        # Create a job for user1
        job_id = self.job_service.create_job(
            self.user1_id, self.tradesman_id, "Test Job", "Test Description",
            total_cost=100
        )
        
        # User1 should be able to delete the job
        assert self.job_service.can_user_edit_job(self.user1_id, job_id) == True
        
        # User2 should not be able to delete the job
        assert self.job_service.can_user_edit_job(self.user2_id, job_id) == False
    
    def test_delete_job_success(self):
        """Test successful deletion of a job"""
        # Create a job for user1
        job_id = self.job_service.create_job(
            self.user1_id, self.tradesman_id, "Test Job", "Test Description",
            total_cost=100
        )
        
        # Verify job exists
        job = self.job_service.get_job_by_id(job_id)
        assert job is not None
        
        # Delete the job
        result = self.job_service.delete_job(job_id)
        assert result == True
        
        # Verify job is deleted
        job = self.job_service.get_job_by_id(job_id)
        assert job is None
    
    def test_delete_job_with_rating(self):
        """Test that deleting a job with rating works correctly"""
        # Create a job with rating for user1
        job_id = self.job_service.create_job(
            self.user1_id, self.tradesman_id, "Test Job", "Test Description",
            total_cost=100, rating=5
        )
        
        # Verify job exists with rating
        job = self.job_service.get_job_by_id(job_id)
        assert job is not None
        assert job['rating'] == 5
        
        # Delete the job
        result = self.job_service.delete_job(job_id)
        assert result == True
        
        # Verify job is deleted
        job = self.job_service.get_job_by_id(job_id)
        assert job is None
    
    def test_delete_nonexistent_job(self):
        """Test that deleting a nonexistent job returns False"""
        # Try to delete a job that doesn't exist
        result = self.job_service.delete_job(99999)
        assert result == False 