import secrets
import datetime
from typing import Optional, List, Dict, Any
from app.services.database import get_db_service
from app.services.email_service import EmailService
from app.services.user_service import UserService

class InvitationService:
    """Service for managing group invitations."""
    
    def __init__(self, group_service=None):
        self.db = get_db_service()
        self.email_service = EmailService()
        self.user_service = UserService()
        self.group_service = group_service
    
    def create_invitation(self, group_id: int, invited_by_user_id: int, email: str, 
                         expires_in_days: int = 7) -> Optional[str]:
        """
        Create a new group invitation.
        
        Args:
            group_id: ID of the group to invite to
            invited_by_user_id: ID of the user sending the invitation
            email: Email address of the invitee
            expires_in_days: Number of days until invitation expires
            
        Returns:
            str: Invitation token if successful, None otherwise
        """
        try:
            # Generate unique token
            token = secrets.token_urlsafe(32)
            
            # Calculate expiration date
            expires_at = datetime.datetime.now() + datetime.timedelta(days=expires_in_days)
            
            # Insert invitation into database
            query = """
                INSERT INTO group_invitations 
                (group_id, invited_by_user_id, email, token, expires_at)
                VALUES (?, ?, ?, ?, ?)
            """
            invitation_id = self.db.execute_insert(query, (
                group_id, invited_by_user_id, email, token, expires_at.isoformat()
            ))
            
            if invitation_id:
                return token
            return None
            
        except Exception as e:
            print(f"Error creating invitation: {e}")
            return None
    
    def get_invitation_by_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Get invitation details by token.
        
        Args:
            token: Invitation token
            
        Returns:
            dict: Invitation details or None if not found/expired
        """
        query = """
            SELECT gi.*, g.name as group_name, g.description as group_description,
                   u.username as inviter_username, u.firstname as inviter_firstname, 
                   u.lastname as inviter_lastname
            FROM group_invitations gi
            JOIN groups g ON gi.group_id = g.id
            JOIN users u ON gi.invited_by_user_id = u.id
            WHERE gi.token = ? AND gi.status = 'pending'
        """
        invitation = self.db.execute_single_query(query, (token,))
        
        if not invitation:
            return None
        
        # Check if invitation has expired
        expires_at = datetime.datetime.fromisoformat(invitation['expires_at'])
        if datetime.datetime.now() > expires_at:
            # Mark as expired
            self._mark_invitation_expired(token)
            return None
        
        return invitation
    
    def accept_invitation(self, token: str, user_id: int) -> bool:
        """
        Accept an invitation and add user to group.
        """
        try:
            invitation = self.get_invitation_by_token(token)
            if not invitation:
                return False
            group_service = self.group_service
            if group_service is None:
                from app.services.group_service import GroupService
                group_service = GroupService()
            existing_membership = group_service.get_user_group_membership(
                user_id, invitation['group_id']
            )
            if existing_membership:
                # User is already in the group, just mark invitation as accepted
                self._mark_invitation_accepted(token)
                return True  # Always return True if already a member
            # Add user to group
            if group_service.add_user_to_group(user_id, invitation['group_id'], 'member'):
                self._mark_invitation_accepted(token)
                return True
            return False
        except Exception as e:
            print(f"Error accepting invitation: {e}")
            return False
    
    def send_invitation_email(self, group_id: int, invited_by_user_id: int, 
                            email: str) -> bool:
        """
        Create and send an invitation email.
        
        Args:
            group_id: ID of the group
            invited_by_user_id: ID of the user sending the invitation
            email: Email address of the invitee
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # Validate inputs
            if not group_id or not invited_by_user_id or not email:
                print(f"Invalid inputs: group_id={group_id}, invited_by_user_id={invited_by_user_id}, email={email}")
                return False
            
            # Get group and inviter details
            group_query = "SELECT name FROM groups WHERE id = ?"
            group = self.db.execute_single_query(group_query, (group_id,))
            
            user_query = "SELECT firstname, lastname FROM users WHERE id = ?"
            user = self.db.execute_single_query(user_query, (invited_by_user_id,))
            
            if not group:
                print(f"Group not found with ID: {group_id}")
                return False
                
            if not user:
                print(f"User not found with ID: {invited_by_user_id}")
                return False
            
            # Create invitation
            token = self.create_invitation(group_id, invited_by_user_id, email)
            if not token:
                print("Failed to create invitation")
                return False
            
            # Get invitation details for email
            invitation = self.get_invitation_by_token(token)
            if not invitation:
                print("Failed to retrieve invitation after creation")
                return False
            
            # Send email
            inviter_name = f"{user['firstname']} {user['lastname']}"
            expires_at = datetime.datetime.fromisoformat(invitation['expires_at'])
            expires_str = expires_at.strftime("%B %d, %Y at %I:%M %p")
            
            return self.email_service.send_group_invitation(
                email, group['name'], inviter_name, token, expires_str
            )
            
        except Exception as e:
            print(f"Error sending invitation email: {e}")
            return False
    
    def get_pending_invitations_for_group(self, group_id: int) -> List[Dict[str, Any]]:
        """
        Get all pending invitations for a group.
        
        Args:
            group_id: ID of the group
            
        Returns:
            list: List of pending invitations
        """
        query = """
            SELECT gi.*, u.username as inviter_username, u.firstname as inviter_firstname,
                   u.lastname as inviter_lastname
            FROM group_invitations gi
            JOIN users u ON gi.invited_by_user_id = u.id
            WHERE gi.group_id = ? AND gi.status = 'pending'
            ORDER BY gi.created_at DESC
        """
        return self.db.execute_query(query, (group_id,))
    
    def cancel_invitation(self, invitation_id: int, user_id: int) -> bool:
        """
        Cancel an invitation (only by the person who sent it or group admin/creator).
        
        Args:
            invitation_id: ID of the invitation to cancel
            user_id: ID of the user cancelling the invitation
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Check if user has permission to cancel
            query = """
                SELECT gi.*, ug.status as user_status
                FROM group_invitations gi
                LEFT JOIN user_groups ug ON ug.user_id = ? AND ug.group_id = gi.group_id
                WHERE gi.id = ?
            """
            invitation = self.db.execute_single_query(query, (user_id, invitation_id))
            
            if not invitation:
                return False
            
            # User can cancel if they sent the invitation or are admin/creator
            can_cancel = (invitation['invited_by_user_id'] == user_id or 
                         invitation['user_status'] in ['admin', 'creator'])
            
            if not can_cancel:
                return False
            
            # Mark as expired (effectively cancelling it)
            update_query = "UPDATE group_invitations SET status = 'expired' WHERE id = ?"
            return self.db.execute_update(update_query, (invitation_id,)) > 0
            
        except Exception as e:
            print(f"Error cancelling invitation: {e}")
            return False
    
    def _mark_invitation_accepted(self, token: str) -> bool:
        """Mark an invitation as accepted."""
        query = "UPDATE group_invitations SET status = 'accepted' WHERE token = ?"
        return self.db.execute_update(query, (token,)) > 0
    
    def _mark_invitation_expired(self, token: str) -> bool:
        """Mark an invitation as expired."""
        query = "UPDATE group_invitations SET status = 'expired' WHERE token = ?"
        return self.db.execute_update(query, (token,)) > 0 