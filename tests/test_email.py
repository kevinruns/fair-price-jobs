#!/usr/bin/env python3
"""
Email Service Tests
Tests for OAuth-based email functionality including configuration, sending, and error handling.
"""

import unittest
import tempfile
import os
import sys
from unittest.mock import patch, MagicMock
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

from app.services.email_service import EmailService
from app.services.invitation_service import InvitationService
from app.services.database import DatabaseService
from app.services.user_service import UserService
from app.services.group_service import GroupService


class TestEmailService(unittest.TestCase):
    """Test OAuth-based email service functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.email_service = EmailService()
        
        # Mock OAuth configuration for testing
        self.email_service.client_id = 'test_client_id'
        self.email_service.client_secret = 'test_client_secret'
        self.email_service.refresh_token = 'test_refresh_token'
        self.email_service.from_email = 'test@example.com'
        self.email_service.app_url = 'http://localhost:5000'
    
    def test_email_service_initialization(self):
        """Test email service initialization."""
        self.assertIsNotNone(self.email_service)
        self.assertEqual(self.email_service.client_id, 'test_client_id')
        self.assertEqual(self.email_service.client_secret, 'test_client_secret')
        self.assertEqual(self.email_service.refresh_token, 'test_refresh_token')
        self.assertEqual(self.email_service.from_email, 'test@example.com')
    
    def test_is_configured_with_valid_config(self):
        """Test configuration check with valid OAuth settings."""
        self.assertTrue(self.email_service.is_configured())
    
    def test_is_configured_with_invalid_config(self):
        """Test configuration check with invalid OAuth settings."""
        self.email_service.client_id = None
        self.assertFalse(self.email_service.is_configured())
    
    def test_send_group_invitation_with_valid_config(self):
        """Test sending group invitation with valid configuration."""
        with patch.object(self.email_service, '_send_email_oauth') as mock_send:
            mock_send.return_value = True
            
            result = self.email_service.send_group_invitation(
                to_email='invitee@example.com',
                group_name='Test Group',
                inviter_name='John Doe',
                invitation_token='test_token_123',
                expires_at='December 31, 2024 at 11:59 PM'
            )
            
            self.assertTrue(result)
            mock_send.assert_called_once()
            
            # Check that email was called with correct parameters
            call_args = mock_send.call_args
            self.assertEqual(call_args[0][0], 'invitee@example.com')  # to_email
            self.assertIn('Test Group', call_args[0][1])  # subject
            self.assertIn('test_token_123', call_args[0][2])  # body contains token
            self.assertIn('John Doe', call_args[0][2])  # body contains inviter name
    
    def test_send_group_invitation_with_invalid_config(self):
        """Test sending group invitation with invalid configuration."""
        # Clear required configuration
        self.email_service.client_id = None
        self.email_service.client_secret = None
        self.email_service.refresh_token = None
        self.email_service.from_email = None
        
        result = self.email_service.send_group_invitation(
            to_email='invitee@example.com',
            group_name='Test Group',
            inviter_name='John Doe',
            invitation_token='test_token_123',
            expires_at='December 31, 2024 at 11:59 PM'
        )
        
        self.assertFalse(result)
    
    @patch('requests.post')
    def test_send_email_oauth_success(self, mock_post):
        """Test successful OAuth email sending."""
        # Mock OAuth token refresh
        mock_token_response = MagicMock()
        mock_token_response.status_code = 200
        mock_token_response.json.return_value = {
            'access_token': 'test_access_token',
            'expires_in': 3600
        }
        
        # Mock Gmail API response
        mock_gmail_response = MagicMock()
        mock_gmail_response.status_code = 200
        
        # Configure mock to return different responses for token and email
        mock_post.side_effect = [mock_token_response, mock_gmail_response]
        
        result = self.email_service._send_email_oauth(
            to_email='test@example.com',
            subject='Test Subject',
            body='<html><body>Test email</body></html>'
        )
        
        self.assertTrue(result)
        self.assertEqual(mock_post.call_count, 2)  # Token refresh + email send
    
    @patch('requests.post')
    def test_send_email_oauth_token_error(self, mock_post):
        """Test OAuth email sending with token refresh error."""
        # Mock token refresh failure
        mock_post.side_effect = Exception("Token refresh failed")
        
        result = self.email_service._send_email_oauth(
            to_email='test@example.com',
            subject='Test Subject',
            body='<html><body>Test email</body></html>'
        )
        
        self.assertFalse(result)
    
    @patch('requests.post')
    def test_send_email_oauth_gmail_error(self, mock_post):
        """Test OAuth email sending with Gmail API error."""
        # Mock successful token refresh but Gmail API failure
        mock_token_response = MagicMock()
        mock_token_response.status_code = 200
        mock_token_response.json.return_value = {
            'access_token': 'test_access_token',
            'expires_in': 3600
        }
        
        mock_gmail_response = MagicMock()
        mock_gmail_response.status_code = 400
        mock_gmail_response.text = 'Bad Request'
        
        mock_post.side_effect = [mock_token_response, mock_gmail_response]
        
        result = self.email_service._send_email_oauth(
            to_email='test@example.com',
            subject='Test Subject',
            body='<html><body>Test email</body></html>'
        )
        
        self.assertFalse(result)
    
    @patch('requests.post')
    def test_test_connection_success(self, mock_post):
        """Test successful OAuth connection test."""
        # Mock successful token refresh
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'access_token': 'test_access_token',
            'expires_in': 3600
        }
        mock_post.return_value = mock_response
        
        result = self.email_service.test_connection()
        
        self.assertTrue(result)
        mock_post.assert_called_once()
    
    @patch('requests.post')
    def test_test_connection_failure(self, mock_post):
        """Test OAuth connection test failure."""
        # Mock token refresh failure
        mock_post.side_effect = Exception("Connection failed")
        
        result = self.email_service.test_connection()
        
        self.assertFalse(result)
    
    def test_email_content_generation(self):
        """Test that email content is generated correctly."""
        with patch.object(self.email_service, '_send_email_oauth') as mock_send:
            mock_send.return_value = True
            
            self.email_service.send_group_invitation(
                to_email='invitee@example.com',
                group_name='Test Group',
                inviter_name='John Doe',
                invitation_token='test_token_123',
                expires_at='December 31, 2024 at 11:59 PM'
            )
            
            # Get the email body that was sent
            call_args = mock_send.call_args
            email_body = call_args[0][2]  # body parameter
            
            # Check that all required content is present
            self.assertIn('Test Group', email_body)
            self.assertIn('John Doe', email_body)
            self.assertIn('test_token_123', email_body)
            self.assertIn('December 31, 2024 at 11:59 PM', email_body)
            self.assertIn('Accept Invitation', email_body)
            self.assertIn('Jobeco', email_body)
    
    def test_get_configuration_status(self):
        """Test configuration status reporting."""
        status = self.email_service.get_configuration_status()
        
        self.assertTrue(status['oauth_configured'])
        self.assertEqual(status['client_id'], 'Set')
        self.assertEqual(status['client_secret'], 'Set')
        self.assertEqual(status['refresh_token'], 'Set')
        self.assertEqual(status['from_email'], 'test@example.com')
        self.assertEqual(status['app_url'], 'http://localhost:5000')
        self.assertFalse(status['access_token_valid'])  # No token yet


class TestInvitationService(unittest.TestCase):
    """Test invitation service functionality."""
    
    def setUp(self):
        """Set up test database and services."""
        self.db_fd, self.db_path = tempfile.mkstemp()
        self.db_service = DatabaseService(self.db_path)
        self.db_service.init_db()
        
        self.group_service = GroupService()
        self.group_service.db = self.db_service
        
        self.invitation_service = InvitationService(group_service=self.group_service)
        self.invitation_service.db = self.db_service
        
        self.user_service = UserService()
        self.user_service.db = self.db_service
        
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
    
    def tearDown(self):
        """Clean up test database."""
        if hasattr(self, 'db_service'):
            self.db_service.close_connection()
        if hasattr(self, 'db_fd') and hasattr(self, 'db_path'):
            try:
                os.close(self.db_fd)
                os.unlink(self.db_path)
            except (OSError, PermissionError):
                pass  # File might already be closed or deleted
    
    def test_create_invitation(self):
        """Test creating an invitation."""
        token = self.invitation_service.create_invitation(
            group_id=self.test_group,
            invited_by_user_id=self.test_user,
            email='invitee@example.com'
        )
        
        self.assertIsNotNone(token)
        self.assertIsInstance(token, str)
        self.assertGreater(len(token), 20)  # Should be a long token
        
        # Verify invitation was created in database
        invitation = self.invitation_service.get_invitation_by_token(token)
        self.assertIsNotNone(invitation)
        self.assertEqual(invitation['email'], 'invitee@example.com')
        self.assertEqual(invitation['group_id'], self.test_group)
        self.assertEqual(invitation['invited_by_user_id'], self.test_user)
        self.assertEqual(invitation['status'], 'pending')
    
    def test_get_invitation_by_token(self):
        """Test getting invitation by token."""
        token = self.invitation_service.create_invitation(
            group_id=self.test_group,
            invited_by_user_id=self.test_user,
            email='invitee@example.com'
        )
        
        invitation = self.invitation_service.get_invitation_by_token(token)
        
        self.assertIsNotNone(invitation)
        self.assertEqual(invitation['email'], 'invitee@example.com')
        self.assertEqual(invitation['group_name'], 'Test Group')
        self.assertEqual(invitation['inviter_firstname'], 'Test')
        self.assertEqual(invitation['inviter_lastname'], 'User')
    
    def test_get_invitation_invalid_token(self):
        """Test getting invitation with invalid token."""
        invitation = self.invitation_service.get_invitation_by_token('invalid_token')
        self.assertIsNone(invitation)
    
    def test_accept_invitation(self):
        """Test accepting an invitation."""
        # Create invitation for a new email (not yet a user)
        invitee_email = 'invitee@example.com'
        token = self.invitation_service.create_invitation(
            group_id=self.test_group,
            invited_by_user_id=self.test_user,
            email=invitee_email
        )
        
        # Now create the invitee user
        invitee_user = self.user_service.create_user(
            username='invitee',
            firstname='Invitee',
            lastname='User',
            email=invitee_email,
            postcode='12345',
            password='password123'
        )
        
        success = self.invitation_service.accept_invitation(token, invitee_user)
        
        self.assertTrue(success)
        
        # Check that user was added to group
        membership = self.group_service.get_user_group_membership(invitee_user, self.test_group)
        self.assertIsNotNone(membership)
        self.assertEqual(membership['status'], 'member')
    
    def test_accept_invitation_already_member(self):
        """Test accepting invitation when already a member."""
        # Add user to group first
        self.group_service.add_user_to_group(self.test_user, self.test_group, 'member')
        
        token = self.invitation_service.create_invitation(
            group_id=self.test_group,
            invited_by_user_id=self.test_user,
            email=self.user_service.get_user_by_id(self.test_user)['email']
        )
        
        success = self.invitation_service.accept_invitation(token, self.test_user)
        
        self.assertTrue(success)  # Should still succeed and mark invitation as accepted
    
    def test_get_pending_invitations_for_group(self):
        """Test getting pending invitations for a group."""
        # Create multiple invitations
        self.invitation_service.create_invitation(
            group_id=self.test_group,
            invited_by_user_id=self.test_user,
            email='invitee1@example.com'
        )
        
        self.invitation_service.create_invitation(
            group_id=self.test_group,
            invited_by_user_id=self.test_user,
            email='invitee2@example.com'
        )
        
        pending = self.invitation_service.get_pending_invitations_for_group(self.test_group)
        
        self.assertEqual(len(pending), 2)
        emails = [inv['email'] for inv in pending]
        self.assertIn('invitee1@example.com', emails)
        self.assertIn('invitee2@example.com', emails)
    
    def test_cancel_invitation(self):
        """Test canceling an invitation."""
        token = self.invitation_service.create_invitation(
            group_id=self.test_group,
            invited_by_user_id=self.test_user,
            email='invitee@example.com'
        )
        
        # Get invitation ID
        invitation = self.invitation_service.get_invitation_by_token(token)
        invitation_id = invitation['id']
        
        success = self.invitation_service.cancel_invitation(invitation_id, self.test_user)
        
        self.assertTrue(success)
        
        # Verify invitation is no longer retrievable
        retrieved = self.invitation_service.get_invitation_by_token(token)
        self.assertIsNone(retrieved)
    
    @patch('app.services.email_service.EmailService.send_group_invitation')
    def test_send_invitation_email_success(self, mock_send_email):
        """Test successful invitation email sending."""
        mock_send_email.return_value = True
        
        success = self.invitation_service.send_invitation_email(
            group_id=self.test_group,
            invited_by_user_id=self.test_user,
            email='invitee@example.com'
        )
        
        self.assertTrue(success)
        mock_send_email.assert_called_once()
    
    @patch('app.services.email_service.EmailService.send_group_invitation')
    def test_send_invitation_email_failure(self, mock_send_email):
        """Test invitation email sending failure."""
        mock_send_email.return_value = False
        
        success = self.invitation_service.send_invitation_email(
            group_id=self.test_group,
            invited_by_user_id=self.test_user,
            email='invitee@example.com'
        )
        
        self.assertFalse(success)
    
    def test_invitation_expiration(self):
        """Test that expired invitations are not retrievable."""
        token = self.invitation_service.create_invitation(
            group_id=self.test_group,
            invited_by_user_id=self.test_user,
            email='invitee@example.com',
            expires_in_days=0  # Expires immediately
        )
        
        # Try to retrieve expired invitation
        invitation = self.invitation_service.get_invitation_by_token(token)
        self.assertIsNone(invitation)  # Should be None due to expiration


class TestEmailIntegration(unittest.TestCase):
    """Test email integration with invitation workflow."""
    
    def setUp(self):
        """Set up test environment."""
        self.db_fd, self.db_path = tempfile.mkstemp()
        self.db_service = DatabaseService(self.db_path)
        self.db_service.init_db()
        
        self.email_service = EmailService()
        self.invitation_service = InvitationService()
        self.invitation_service.db = self.db_service
        
        self.user_service = UserService()
        self.user_service.db = self.db_service
        
        self.group_service = GroupService()
        self.group_service.db = self.db_service
        
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
    
    def tearDown(self):
        """Clean up test environment."""
        if hasattr(self, 'db_service'):
            self.db_service.close_connection()
        if hasattr(self, 'db_fd') and hasattr(self, 'db_path'):
            try:
                os.close(self.db_fd)
                os.unlink(self.db_path)
            except (OSError, PermissionError):
                pass  # File might already be closed or deleted
    
    @patch('app.services.email_service.EmailService.send_group_invitation')
    def test_full_invitation_workflow(self, mock_send_email):
        """Test complete invitation workflow with email sending."""
        mock_send_email.return_value = True
        
        # Send invitation email
        email_sent = self.invitation_service.send_invitation_email(
            group_id=self.test_group,
            invited_by_user_id=self.test_user,
            email='invitee@example.com'
        )
        
        self.assertTrue(email_sent)
        
        # Verify email was sent with correct parameters
        mock_send_email.assert_called_once()
        call_args = mock_send_email.call_args
        self.assertEqual(call_args[0][0], 'invitee@example.com')  # to_email
        self.assertIn('Test Group', call_args[0][1])  # subject contains group name
        self.assertIn('Test User', call_args[0][2])  # body contains inviter name


def run_email_tests():
    """Run all email-related tests."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestEmailService))
    suite.addTests(loader.loadTestsFromTestCase(TestInvitationService))
    suite.addTests(loader.loadTestsFromTestCase(TestEmailIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_email_tests()
    sys.exit(0 if success else 1) 
