#!/usr/bin/env python3
"""
OAuth-based Email Service for Jobéco Application
This service uses OAuth 2.0 for secure email authentication.
"""

import os
import json
import base64
import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from config import get_config

logger = logging.getLogger(__name__)

class EmailService:
    """OAuth-based email service for secure email sending."""
    
    def __init__(self):
        self.config = get_config()
        self.app_url = getattr(self.config, 'APP_URL', 'http://localhost:5000')
        
        # OAuth configuration
        self.client_id = getattr(self.config, 'OAUTH_CLIENT_ID', None)
        self.client_secret = getattr(self.config, 'OAUTH_CLIENT_SECRET', None)
        self.refresh_token = getattr(self.config, 'OAUTH_REFRESH_TOKEN', None)
        self.from_email = getattr(self.config, 'FROM_EMAIL', None)
        
        # Gmail OAuth endpoints
        self.token_url = 'https://oauth2.googleapis.com/token'
        self.gmail_api_url = 'https://gmail.googleapis.com/gmail/v1/users/me/messages/send'
        
        # Token management
        self.access_token = None
        self.token_expires_at = None
    
    def is_configured(self) -> bool:
        """Check if OAuth is properly configured."""
        return all([
            self.client_id,
            self.client_secret,
            self.refresh_token,
            self.from_email
        ])
    
    def get_access_token(self) -> Optional[str]:
        """Get a valid access token, refreshing if necessary."""
        if not self.is_configured():
            logger.error("OAuth not properly configured")
            return None
        
        # Check if we have a valid token
        if (self.access_token and self.token_expires_at and 
            datetime.now() < self.token_expires_at):
            return self.access_token
        
        # Refresh the token
        return self._refresh_access_token()
    
    def _refresh_access_token(self) -> Optional[str]:
        """Refresh the OAuth access token."""
        try:
            data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'refresh_token': self.refresh_token,
                'grant_type': 'refresh_token'
            }
            
            response = requests.post(self.token_url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data['access_token']
            
            # Set expiration (subtract 5 minutes for safety)
            expires_in = token_data.get('expires_in', 3600)
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 300)
            
            logger.info("OAuth access token refreshed successfully")
            return self.access_token
            
        except Exception as e:
            logger.error(f"Failed to refresh OAuth token: {e}")
            return None
    
    def send_group_invitation(self, to_email: str, group_name: str, inviter_name: str, 
                            invitation_token: str, expires_at: str) -> bool:
        """
        Send a group invitation email using OAuth.
        
        Args:
            to_email: Email address of the invitee
            group_name: Name of the group being invited to
            inviter_name: Name of the person sending the invitation
            invitation_token: Unique token for the invitation
            expires_at: When the invitation expires
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        if not self.is_configured():
            logger.warning("OAuth email configuration incomplete. Cannot send invitation.")
            return False
        
        subject = f"Invitation to join {group_name}"
        
        # Create the invitation URL
        invitation_url = f"{self.app_url}/invitation/{invitation_token}"
        
        # Email body
        body = f"""
        <html>
        <body>
            <h2>You're invited to join {group_name}!</h2>
            <p>Hello,</p>
            <p>{inviter_name} has invited you to join the group <strong>{group_name}</strong> on Jobéco.</p>
            <p>Jobéco is a platform where you can share and discover trusted tradesmen with your community.</p>
            <p><strong>To accept this invitation, click the link below:</strong></p>
            <p><a href="{invitation_url}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Accept Invitation</a></p>
            <p>Or copy and paste this URL into your browser:</p>
            <p>{invitation_url}</p>
            <p><strong>This invitation expires on: {expires_at}</strong></p>
            <p>If you don't have an account yet, you'll be able to create one when you accept the invitation.</p>
            <p>Best regards,<br>The Jobéco Team</p>
        </body>
        </html>
        """
        
        return self._send_email_oauth(to_email, subject, body)
    
    def _send_email_oauth(self, to_email: str, subject: str, body: str) -> bool:
        """
        Send an email using Gmail API with OAuth.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body (HTML)
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            access_token = self.get_access_token()
            if not access_token:
                logger.error("Failed to get OAuth access token")
                return False
            
            # Create email message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.from_email
            message["To"] = to_email
            
            # Add HTML body
            html_part = MIMEText(body, "html")
            message.attach(html_part)
            
            # Encode message for Gmail API
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            # Send via Gmail API
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'raw': raw_message
            }
            
            response = requests.post(
                self.gmail_api_url,
                headers=headers,
                json=data
            )
            
            if response.status_code == 200:
                logger.info(f"Email sent successfully to {to_email}")
                return True
            else:
                logger.error(f"Failed to send email: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    def test_connection(self) -> bool:
        """Test the OAuth configuration by attempting to get an access token."""
        try:
            if not self.is_configured():
                logger.error("OAuth not properly configured")
                return False
            
            access_token = self.get_access_token()
            if access_token:
                logger.info("OAuth connection test successful")
                return True
            else:
                logger.error("OAuth connection test failed")
                return False
                
        except Exception as e:
            logger.error(f"OAuth connection test failed: {str(e)}")
            return False
    
    def get_configuration_status(self) -> Dict[str, Any]:
        """Get the current OAuth configuration status."""
        return {
            'oauth_configured': self.is_configured(),
            'client_id': 'Set' if self.client_id else 'Not set',
            'client_secret': 'Set' if self.client_secret else 'Not set',
            'refresh_token': 'Set' if self.refresh_token else 'Not set',
            'from_email': self.from_email or 'Not set',
            'app_url': self.app_url,
            'access_token_valid': bool(self.access_token and self.token_expires_at and 
                                     datetime.now() < self.token_expires_at)
        } 
