import unittest
import tempfile
import os
from app.services.database import DatabaseService
from app.services.user_service import UserService
from app.services.group_service import GroupService
from app.services.invitation_service import InvitationService
from main import create_app


class TestInvitationFlow(unittest.TestCase):
    """Test the invitation flow that redirects to registration."""
    
    def setUp(self):
        """Set up test environment."""
        self.db_fd, self.db_path = tempfile.mkstemp()
        self.db_service = DatabaseService(self.db_path)
        self.db_service.init_db()
        
        self.user_service = UserService()
        self.user_service.db = self.db_service
        
        self.group_service = GroupService()
        self.group_service.db = self.db_service
        
        self.invitation_service = InvitationService()
        self.invitation_service.db = self.db_service
        self.invitation_service.group_service = self.group_service
        
        # Create test user and group
        self.test_user = self.user_service.create_user(
            username='testuser',
            firstname='Test',
            lastname='User',
            email='test@example.com',
            postcode='12345',
            password='password123'
        )
        
        self.test_group = self.group_service.create_group('Test Group', '12345')
        
        # Add the creator to the group
        self.group_service.add_user_to_group(self.test_user, self.test_group, 'creator')
        
        # Create Flask app for testing
        os.environ['TEST_DATABASE'] = self.db_path
        self.app = create_app('testing')
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def tearDown(self):
        """Clean up test environment."""
        if hasattr(self, 'db_service'):
            self.db_service.close_connection()
        if hasattr(self, 'db_fd') and hasattr(self, 'db_path'):
            try:
                os.close(self.db_fd)
                os.unlink(self.db_path)
            except (OSError, PermissionError):
                pass
    
    def test_invitation_redirects_to_registration(self):
        """Test that invitation link redirects to registration with invitation info."""
        # Create an invitation
        token = self.invitation_service.create_invitation(
            group_id=self.test_group,
            invited_by_user_id=self.test_user,
            email='newuser@example.com'
        )
        
        # Debug: Check if invitation was created
        print(f"Created token: {token}")
        invitation = self.invitation_service.get_invitation_by_token(token)
        print(f"Retrieved invitation: {invitation}")
        
        # Access the invitation URL
        response = self.client.get(f'/invitation/{token}')
        
        print(f"Response status: {response.status_code}")
        print(f"Response location: {response.location}")
        
        # Should redirect to registration
        self.assertEqual(response.status_code, 302)
        self.assertIn('/register', response.location)
        self.assertIn('invitation_token', response.location)
    
    def test_registration_with_invitation_shows_message(self):
        """Test that registration page shows invitation message when accessed with invitation token."""
        # Create an invitation
        token = self.invitation_service.create_invitation(
            group_id=self.test_group,
            invited_by_user_id=self.test_user,
            email='newuser@example.com'
        )
        
        # Access registration with invitation token
        response = self.client.get(f'/register?invitation_token={token}')
        
        # Should show invitation message
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'You have been invited to join Test Group!', response.data)
        self.assertIn(b'Please register to continue and automatically join the group', response.data)
    
    def test_registration_without_invitation_shows_normal_form(self):
        """Test that registration page shows normal form without invitation."""
        response = self.client.get('/register')
        
        # Should not show invitation message
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b'You have been invited to join', response.data)
        self.assertIn(b'Register', response.data)
    
    def test_invalid_invitation_token_ignored(self):
        """Test that invalid invitation token is ignored."""
        response = self.client.get('/register?invitation_token=invalid_token')
        
        # Should not show invitation message
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b'You have been invited to join', response.data)
        self.assertIn(b'Register', response.data)


if __name__ == '__main__':
    unittest.main() 