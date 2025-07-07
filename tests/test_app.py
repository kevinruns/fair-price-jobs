#!/usr/bin/env python3
"""
Comprehensive test script for Fair Price application
Tests services, routes, and database operations
"""

import unittest
import tempfile
import os
import sys
from datetime import datetime

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.services.database import DatabaseService
from app.services.user_service import UserService
from app.services.group_service import GroupService
from app.services.tradesman_service import TradesmanService
from app.services.job_service import JobService


class TestDatabaseService(unittest.TestCase):
    """Test database service functionality"""
    
    def setUp(self):
        """Set up test database"""
        self.db_fd, self.db_path = tempfile.mkstemp()
        self.db_service = DatabaseService(self.db_path)
        self.db_service.init_db()
    
    def tearDown(self):
        """Clean up test database"""
        self.db_service.close_connection()
        os.close(self.db_fd)
        os.unlink(self.db_path)
    
    def test_database_initialization(self):
        """Test database initialization"""
        # Check if tables exist
        tables = self.db_service.execute_query(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        table_names = [table['name'] for table in tables]
        
        expected_tables = ['users', 'groups', 'tradesmen', 'jobs', 'user_groups', 'group_tradesmen', 'user_tradesmen']
        for table in expected_tables:
            self.assertIn(table, table_names)
    
    def test_execute_query(self):
        """Test query execution"""
        result = self.db_service.execute_query("SELECT 1 as test")
        self.assertEqual(result[0]['test'], 1)
    
    def test_execute_single_query(self):
        """Test single query execution"""
        result = self.db_service.execute_single_query("SELECT 1 as test")
        self.assertEqual(result['test'], 1)
    
    def test_execute_insert(self):
        """Test insert execution"""
        user_id = self.db_service.execute_insert(
            "INSERT INTO users (username, firstname, lastname, email, postcode, hash) VALUES (?, ?, ?, ?, ?, ?)",
            ('testuser', 'Test', 'User', 'test@example.com', '12345', 'hash123')
        )
        self.assertIsInstance(user_id, int)
        self.assertGreater(user_id, 0)


class TestUserService(unittest.TestCase):
    """Test user service functionality"""
    
    def setUp(self):
        """Set up test database and user service"""
        self.db_fd, self.db_path = tempfile.mkstemp()
        self.db_service = DatabaseService(self.db_path)
        self.db_service.init_db()
        self.user_service = UserService()
        self.user_service.db = self.db_service
    
    def tearDown(self):
        """Clean up test database"""
        self.db_service.close_connection()
        os.close(self.db_fd)
        os.unlink(self.db_path)
    
    def test_create_user(self):
        """Test user creation"""
        user_id = self.user_service.create_user(
            username='testuser',
            firstname='Test',
            lastname='User',
            email='test@example.com',
            postcode='12345',
            password='password123'
        )
        self.assertIsInstance(user_id, int)
        self.assertGreater(user_id, 0)
    
    def test_get_user_by_id(self):
        """Test getting user by ID"""
        # Create a user first
        user_id = self.user_service.create_user(
            username='testuser',
            firstname='Test',
            lastname='User',
            email='test@example.com',
            postcode='12345',
            password='password123'
        )
        
        # Get the user
        user = self.user_service.get_user_by_id(user_id)
        self.assertIsNotNone(user)
        self.assertEqual(user['username'], 'testuser')
        self.assertEqual(user['firstname'], 'Test')
        self.assertEqual(user['lastname'], 'User')
    
    def test_get_user_by_username(self):
        """Test getting user by username"""
        # Create a user first
        self.user_service.create_user(
            username='testuser',
            firstname='Test',
            lastname='User',
            email='test@example.com',
            postcode='12345',
            password='password123'
        )
        
        # Get the user
        user = self.user_service.get_user_by_username('testuser')
        self.assertIsNotNone(user)
        self.assertEqual(user['username'], 'testuser')
    
    def test_verify_password(self):
        """Test password verification"""
        # Create a user first
        self.user_service.create_user(
            username='testuser',
            firstname='Test',
            lastname='User',
            email='test@example.com',
            postcode='12345',
            password='password123'
        )
        
        # Verify correct password
        user = self.user_service.authenticate_user('testuser', 'password123')
        self.assertIsNotNone(user)
        self.assertEqual(user['username'], 'testuser')
        
        # Verify incorrect password
        user = self.user_service.authenticate_user('testuser', 'wrongpassword')
        self.assertIsNone(user)


class TestGroupService(unittest.TestCase):
    """Test group service functionality"""
    
    def setUp(self):
        """Set up test database and services"""
        self.db_fd, self.db_path = tempfile.mkstemp()
        self.db_service = DatabaseService(self.db_path)
        self.db_service.init_db()
        self.group_service = GroupService()
        self.group_service.db = self.db_service
        self.user_service = UserService()
        self.user_service.db = self.db_service
    
    def tearDown(self):
        """Clean up test database"""
        self.db_service.close_connection()
        os.close(self.db_fd)
        os.unlink(self.db_path)
    
    def test_create_group(self):
        """Test group creation"""
        group_id = self.group_service.create_group('Test Group', '12345')
        self.assertIsInstance(group_id, int)
        self.assertGreater(group_id, 0)
    
    def test_create_group_with_description(self):
        """Test group creation with description"""
        description = "This is a test group for testing purposes"
        group_id = self.group_service.create_group('Test Group', '12345', description)
        self.assertIsInstance(group_id, int)
        self.assertGreater(group_id, 0)
        
        # Verify the group was created with description
        group = self.group_service.get_group_by_id(group_id)
        self.assertIsNotNone(group)
        self.assertEqual(group['name'], 'Test Group')
        self.assertEqual(group['postcode'], '12345')
        self.assertEqual(group['description'], description)
    
    def test_create_group_without_description(self):
        """Test group creation without description (should be None)"""
        group_id = self.group_service.create_group('Test Group', '12345')
        self.assertIsInstance(group_id, int)
        self.assertGreater(group_id, 0)
        
        # Verify the group was created without description
        group = self.group_service.get_group_by_id(group_id)
        self.assertIsNotNone(group)
        self.assertEqual(group['name'], 'Test Group')
        self.assertEqual(group['postcode'], '12345')
        self.assertIsNone(group['description'])
    
    def test_create_group_with_empty_description(self):
        """Test group creation with empty description (should be None)"""
        group_id = self.group_service.create_group('Test Group', '12345', '')
        self.assertIsInstance(group_id, int)
        self.assertGreater(group_id, 0)
        
        # Verify the group was created without description
        group = self.group_service.get_group_by_id(group_id)
        self.assertIsNotNone(group)
        self.assertEqual(group['name'], 'Test Group')
        self.assertEqual(group['postcode'], '12345')
        self.assertIsNone(group['description'])
    
    def test_get_group_by_id(self):
        """Test getting group by ID"""
        # Create a group first
        group_id = self.group_service.create_group('Test Group', '12345')
        
        # Get the group
        group = self.group_service.get_group_by_id(group_id)
        self.assertIsNotNone(group)
        self.assertEqual(group['name'], 'Test Group')
        self.assertEqual(group['postcode'], '12345')
    
    def test_add_user_to_group(self):
        """Test adding user to group"""
        # Create user and group
        user_id = self.user_service.create_user(
            username='testuser',
            firstname='Test',
            lastname='User',
            email='test@example.com',
            postcode='12345',
            password='password123'
        )
        group_id = self.group_service.create_group('Test Group', '12345')
        
        # Add user to group
        self.group_service.add_user_to_group(user_id, group_id, 'member')
        
        # Verify membership
        membership = self.group_service.get_user_group_membership(user_id, group_id)
        self.assertIsNotNone(membership)
        self.assertEqual(membership['status'], 'member')
    
    def test_get_group_members(self):
        """Test getting group members"""
        # Create user and group
        user_id = self.user_service.create_user(
            username='testuser',
            firstname='Test',
            lastname='User',
            email='test@example.com',
            postcode='12345',
            password='password123'
        )
        group_id = self.group_service.create_group('Test Group', '12345')
        
        # Add user to group
        self.group_service.add_user_to_group(user_id, group_id, 'member')
        
        # Get group members
        members = self.group_service.get_group_members(group_id)
        self.assertEqual(len(members), 1)
        self.assertEqual(members[0]['username'], 'testuser')
    
    def test_get_group_member_count(self):
        """Test getting group member count"""
        # Create users and group
        user1_id = self.user_service.create_user(
            username='user1',
            firstname='User',
            lastname='One',
            email='user1@example.com',
            postcode='12345',
            password='password123'
        )
        user2_id = self.user_service.create_user(
            username='user2',
            firstname='User',
            lastname='Two',
            email='user2@example.com',
            postcode='12345',
            password='password123'
        )
        group_id = self.group_service.create_group('Test Group', '12345')
        
        # Initially no members
        member_count = self.group_service.get_group_member_count(group_id)
        self.assertEqual(member_count, 0)
        
        # Add first user to group
        self.group_service.add_user_to_group(user1_id, group_id, 'member')
        member_count = self.group_service.get_group_member_count(group_id)
        self.assertEqual(member_count, 1)
        
        # Add second user to group
        self.group_service.add_user_to_group(user2_id, group_id, 'member')
        member_count = self.group_service.get_group_member_count(group_id)
        self.assertEqual(member_count, 2)
        
        # Add a pending user (should not count)
        user3_id = self.user_service.create_user(
            username='user3',
            firstname='User',
            lastname='Three',
            email='user3@example.com',
            postcode='12345',
            password='password123'
        )
        self.group_service.add_user_to_group(user3_id, group_id, 'pending')
        member_count = self.group_service.get_group_member_count(group_id)
        self.assertEqual(member_count, 2)  # Still 2, pending doesn't count

    def test_create_group_with_creator(self):
        """Test creating a group with creator in a single transaction."""
        # Create a test user first
        user_id = self.user_service.create_user(
            username='testuser',
            firstname='Test',
            lastname='User',
            email='test@example.com',
            postcode='12345',
            password='password123'
        )
        
        # Create group with creator
        group_id = self.group_service.create_group_with_creator(
            name='Test Group',
            postcode='12345',
            creator_user_id=user_id,
            description='Test description'
        )
        
        # Verify group was created
        group = self.group_service.get_group_by_id(group_id)
        self.assertIsNotNone(group)
        self.assertEqual(group['name'], 'Test Group')
        self.assertEqual(group['postcode'], '12345')
        self.assertEqual(group['description'], 'Test description')
        
        # Verify creator was added to group
        membership = self.group_service.get_user_group_membership(user_id, group_id)
        self.assertIsNotNone(membership)
        self.assertEqual(membership['status'], 'creator')
        
        # Verify group member count
        member_count = self.group_service.get_group_member_count(group_id)
        self.assertEqual(member_count, 1)


class TestTradesmanService(unittest.TestCase):
    """Test tradesman service functionality"""
    
    def setUp(self):
        """Set up test database and services"""
        self.db_fd, self.db_path = tempfile.mkstemp()
        self.db_service = DatabaseService(self.db_path)
        self.db_service.init_db()
        self.tradesman_service = TradesmanService()
        self.tradesman_service.db = self.db_service
        self.user_service = UserService()
        self.user_service.db = self.db_service
    
    def tearDown(self):
        """Clean up test database"""
        self.db_service.close_connection()
        os.close(self.db_fd) 


class TestJobService(unittest.TestCase):
    """Test job service functionality"""
    
    def setUp(self):
        """Set up test database and services"""
        self.db_fd, self.db_path = tempfile.mkstemp()
        self.db_service = DatabaseService(self.db_path)
        self.db_service.init_db()
        self.job_service = JobService()
        self.job_service.db = self.db_service
        self.user_service = UserService()
        self.user_service.db = self.db_service
    
    def tearDown(self):
        """Clean up test database"""
        self.db_service.close_connection()
        os.close(self.db_fd) 


class TestIntegration(unittest.TestCase):
    """Test integration of services"""
    
    def setUp(self):
        """Set up test database and services"""
        self.db_fd, self.db_path = tempfile.mkstemp()
        self.db_service = DatabaseService(self.db_path)
        self.db_service.init_db()
        self.user_service = UserService()
        self.user_service.db = self.db_service
        self.group_service = GroupService()
        self.group_service.db = self.db_service
        self.tradesman_service = TradesmanService()
        self.tradesman_service.db = self.db_service
        self.job_service = JobService()
        self.job_service.db = self.db_service
    
    def tearDown(self):
        """Clean up test database"""
        self.db_service.close_connection()
        os.close(self.db_fd)
        os.unlink(self.db_path)
    
    def test_create_user_and_group(self):
        """Test creating a user and adding them to a group"""
        user_id = self.user_service.create_user(
            username='testuser',
            firstname='Test',
            lastname='User',
            email='test@example.com',
            postcode='12345',
            password='password123'
        )
        group_id = self.group_service.create_group('Test Group', '12345')
        # Explicitly add user to group
        self.group_service.add_user_to_group(user_id, group_id, 'member')
        membership = self.group_service.get_user_group_membership(user_id, group_id)
        self.assertIsNotNone(membership)
        self.assertEqual(membership['status'], 'member')

    def test_create_tradesman(self):
        """Test creating a tradesman and associating with user"""
        user_id = self.user_service.create_user(
            username='tradesmanuser',
            firstname='Tradesman',
            lastname='User',
            email='tradesman@example.com',
            postcode='12345',
            password='password123'
        )
        tradesman_id = self.tradesman_service.create_tradesman(
            trade='Plumber',
            first_name='Tradesman',
            family_name='User',
            company_name='Smith Plumbing',
            address='123 Main St',
            postcode='12345',
            phone_number='123-456-7890',
            email='tradesman@example.com'
        )
        # Associate tradesman with user
        self.tradesman_service.add_user_tradesman_relationship(user_id, tradesman_id)
        user_tradesmen = self.tradesman_service.get_tradesmen_by_user(user_id)
        self.assertIsNotNone(user_tradesmen)
        self.assertEqual(len(user_tradesmen), 1)
        self.assertEqual(user_tradesmen[0]['first_name'], 'Tradesman')
        self.assertEqual(user_tradesmen[0]['family_name'], 'User')
        self.assertEqual(user_tradesmen[0]['email'], 'tradesman@example.com')
        self.assertEqual(user_tradesmen[0]['postcode'], '12345')
        self.assertEqual(user_tradesmen[0]['phone_number'], '123-456-7890')

    def test_create_job(self):
        """Test creating a job"""
        user_id = self.user_service.create_user(
            username='jobuser',
            firstname='Job',
            lastname='User',
            email='job@example.com',
            postcode='12345',
            password='password123'
        )
        tradesman_id = self.tradesman_service.create_tradesman(
            trade='Plumber',
            first_name='John',
            family_name='Smith',
            company_name='Smith Plumbing',
            address='123 Main St',
            postcode='12345',
            phone_number='555-1234',
            email='john@smithplumbing.com'
        )
        # Associate tradesman with user
        self.tradesman_service.add_user_tradesman_relationship(user_id, tradesman_id)
        job_id = self.job_service.create_job(
            user_id=user_id,
            tradesman_id=tradesman_id,
            title='Test Job',
            description='This is a test job',
            date_started='2024-01-01',
            date_finished='2024-01-02',
            total_cost=1000,
            rating=5
        )
        self.assertIsInstance(job_id, int)
        self.assertGreater(job_id, 0)
        user_jobs = self.job_service.get_jobs_by_user(user_id)
        self.assertIsNotNone(user_jobs)
        self.assertTrue(any(job['id'] == job_id for job in user_jobs))


def run_tests():
    """Run all tests"""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestDatabaseService,
        TestUserService,
        TestGroupService,
        TestTradesmanService,
        TestJobService,
        TestIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"Test Summary:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print(f"{'='*50}")
    
    return result

if __name__ == '__main__':
    print("Running Fair Price Application Tests...")
    print("="*50)
    
    success = run_tests()
    
    if success.wasSuccessful():
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1) 