import pytest
import tempfile
import os
from app.services.invitation_service import InvitationService
from app.services.group_service import GroupService
from app.services.user_service import UserService
from app.services.database import DatabaseService
from main import create_app

class TestInvitations:
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
            self.invitation_service = InvitationService()
            self.group_service = GroupService()
            self.user_service = UserService()
            
            # Create test users
            self.user1_id = self.user_service.create_user("testuser1", "Test", "User1", "test1@example.com", "12345", "password123")
            self.user2_id = self.user_service.create_user("testuser2", "Test", "User2", "test2@example.com", "12345", "password123")
            
            # Create a test group
            self.group_id = self.group_service.create_group("Test Group", "12345", "Test Description")
            self.group_service.add_user_to_group(self.user1_id, self.group_id, "creator")
            
            yield
        
        # Clean up the temporary database file
        try:
            os.unlink(self.temp_db_path)
        except OSError:
            pass  # File might already be deleted
    
    def test_create_invitation(self):
        """Test creating a new invitation"""
        token = self.invitation_service.create_invitation(
            self.group_id, self.user1_id, "invitee@example.com"
        )
        
        assert token is not None
        assert len(token) > 20  # Token should be reasonably long
        
        # Verify invitation was created in database
        invitation = self.invitation_service.get_invitation_by_token(token)
        assert invitation is not None
        assert invitation['email'] == "invitee@example.com"
        assert invitation['group_id'] == self.group_id
        assert invitation['invited_by_user_id'] == self.user1_id
        assert invitation['status'] == 'pending'
    
    def test_get_invitation_by_token(self):
        """Test retrieving invitation by token"""
        token = self.invitation_service.create_invitation(
            self.group_id, self.user1_id, "invitee@example.com"
        )
        
        invitation = self.invitation_service.get_invitation_by_token(token)
        assert invitation is not None
        assert invitation['email'] == "invitee@example.com"
        assert invitation['group_name'] == "Test Group"
        assert invitation['inviter_firstname'] == "Test"
        assert invitation['inviter_lastname'] == "User1"
    
    def test_get_invitation_invalid_token(self):
        """Test retrieving invitation with invalid token"""
        invitation = self.invitation_service.get_invitation_by_token("invalid_token")
        assert invitation is None
    
    def test_accept_invitation(self):
        """Test accepting an invitation"""
        token = self.invitation_service.create_invitation(
            self.group_id, self.user1_id, "invitee@example.com"
        )
        
        # Accept invitation for user2
        success = self.invitation_service.accept_invitation(token, self.user2_id)
        assert success == True
        
        # Verify user2 is now a member of the group
        membership = self.group_service.get_user_group_membership(self.user2_id, self.group_id)
        assert membership is not None
        assert membership['status'] == 'member'
        
        # Verify invitation is marked as accepted
        invitation = self.invitation_service.get_invitation_by_token(token)
        assert invitation is None  # Should not be found as it's now accepted
    
    def test_accept_invitation_already_member(self):
        """Test accepting invitation when user is already a member"""
        # Add user2 to group first
        self.group_service.add_user_to_group(self.user2_id, self.group_id, "member")
        
        token = self.invitation_service.create_invitation(
            self.group_id, self.user1_id, "invitee@example.com"
        )
        
        # Accept invitation for user2 (already a member)
        success = self.invitation_service.accept_invitation(token, self.user2_id)
        assert success == True  # Should still succeed and mark invitation as accepted
    
    def test_get_pending_invitations_for_group(self):
        """Test getting pending invitations for a group"""
        # Create multiple invitations
        self.invitation_service.create_invitation(
            self.group_id, self.user1_id, "invitee1@example.com"
        )
        self.invitation_service.create_invitation(
            self.group_id, self.user1_id, "invitee2@example.com"
        )
        
        invitations = self.invitation_service.get_pending_invitations_for_group(self.group_id)
        assert len(invitations) == 2
        assert invitations[0]['email'] in ["invitee1@example.com", "invitee2@example.com"]
        assert invitations[1]['email'] in ["invitee1@example.com", "invitee2@example.com"]
    
    def test_cancel_invitation(self):
        """Test cancelling an invitation"""
        token = self.invitation_service.create_invitation(
            self.group_id, self.user1_id, "invitee@example.com"
        )
        
        # Get invitation ID
        invitation = self.invitation_service.get_invitation_by_token(token)
        invitation_id = invitation['id']
        
        # Cancel invitation
        success = self.invitation_service.cancel_invitation(invitation_id, self.user1_id)
        assert success == True
        
        # Verify invitation is no longer pending
        invitation = self.invitation_service.get_invitation_by_token(token)
        assert invitation is None 