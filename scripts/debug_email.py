#!/usr/bin/env python3
"""
Debug Email Script
Helps identify issues with email sending by providing detailed debugging information.
"""

import os
import sys
import base64
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.email_service import EmailService

def debug_email_sending():
    """Debug email sending with detailed information."""
    print("🔍 Email Debug Script")
    print("=" * 50)
    
    # Initialize email service
    email_service = EmailService()
    
    # Check configuration
    print("\n📋 Configuration Check:")
    config_status = email_service.get_configuration_status()
    for key, value in config_status.items():
        print(f"  {key}: {value}")
    
    if not email_service.is_configured():
        print("\n❌ Email service not properly configured!")
        return
    
    # Test OAuth connection
    print("\n🔗 Testing OAuth Connection:")
    if email_service.test_connection():
        print("  ✅ OAuth connection successful")
    else:
        print("  ❌ OAuth connection failed")
        return
    
    # Test with minimal email
    print("\n📧 Testing with minimal email:")
    test_email = input("Enter test email address: ").strip()
    if not test_email:
        print("  ❌ No email address provided")
        return
    
    # Create a simple test message
    subject = "Test Email"
    body = "<html><body><h1>Test</h1><p>This is a test email.</p></body></html>"
    
    print(f"\n📝 Test Message Details:")
    print(f"  To: {test_email}")
    print(f"  From: {email_service.from_email}")
    print(f"  Subject: {subject}")
    print(f"  Body length: {len(body)} characters")
    
    # Debug the message creation
    print(f"\n🔧 Message Creation Debug:")
    try:
        # Create email message
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = email_service.from_email
        message["To"] = test_email
        
        # Add HTML body
        html_part = MIMEText(body, "html")
        message.attach(html_part)
        
        print(f"  ✅ Message created successfully")
        print(f"  Message headers: {dict(message.items())}")
        
        # Encode message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        print(f"  ✅ Message encoded successfully")
        print(f"  Encoded length: {len(raw_message)} characters")
        
        # Test the actual sending
        print(f"\n📤 Attempting to send email...")
        success = email_service._send_email_oauth(test_email, subject, body)
        
        if success:
            print("  ✅ Email sent successfully!")
        else:
            print("  ❌ Email sending failed")
            
    except Exception as e:
        print(f"  ❌ Error during message creation: {e}")
        import traceback
        traceback.print_exc()

def debug_invitation_email():
    """Debug invitation email specifically."""
    print("\n🎯 Debugging Invitation Email:")
    print("=" * 50)
    
    email_service = EmailService()
    
    if not email_service.is_configured():
        print("❌ Email service not configured")
        return
    
    # Test invitation email
    test_email = input("Enter test email address for invitation: ").strip()
    if not test_email:
        print("❌ No email address provided")
        return
    
    print(f"\n📧 Sending test invitation...")
    success = email_service.send_group_invitation(
        to_email=test_email,
        group_name="Test Group",
        inviter_name="Test User",
        invitation_token="test_token_123",
        expires_at="December 31, 2024 at 11:59 PM"
    )
    
    if success:
        print("✅ Invitation email sent successfully!")
    else:
        print("❌ Invitation email failed")

def check_oauth_scopes():
    """Check if OAuth scopes are properly configured."""
    print("\n🔍 OAuth Scope Check:")
    print("=" * 50)
    
    print("Required OAuth scopes for Gmail API:")
    print("  - https://www.googleapis.com/auth/gmail.send")
    print("  - https://www.googleapis.com/auth/gmail.compose")
    
    print("\nTo check your current scopes:")
    print("1. Go to Google Cloud Console")
    print("2. Navigate to APIs & Services > OAuth consent screen")
    print("3. Check the 'Scopes' section")
    print("4. Ensure the required scopes are listed")

if __name__ == "__main__":
    print("Choose debug option:")
    print("1. Debug general email sending")
    print("2. Debug invitation email")
    print("3. Check OAuth scopes")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        debug_email_sending()
    elif choice == "2":
        debug_invitation_email()
    elif choice == "3":
        check_oauth_scopes()
    else:
        print("Invalid choice") 