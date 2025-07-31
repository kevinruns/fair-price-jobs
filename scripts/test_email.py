#!/usr/bin/env python3
"""
OAuth Email Configuration Test Script
This script tests the OAuth configuration for the Job�co application.
"""

import os
import sys
from pathlib import Path

# Get the project root directory (parent of scripts directory)
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_oauth_configuration():
    """Test OAuth configuration and connection."""
    print("Job�co - OAuth Email Configuration Test")
    print("=" * 40)
    
    try:
        from app.services.email_service import EmailService
        from config import get_config
        
        # Get configuration
        config = get_config()
        email_service = EmailService()
        
        print("\n📧 OAuth Configuration:")
        print(f"OAuth Client ID: {'✅ Set' if email_service.client_id else '❌ Not set'}")
        print(f"OAuth Client Secret: {'✅ Set' if email_service.client_secret else '❌ Not set'}")
        print(f"OAuth Refresh Token: {'✅ Set' if email_service.refresh_token else '❌ Not set'}")
        print(f"From Email: {email_service.from_email or '❌ Not set'}")
        print(f"App URL: {email_service.app_url}")
        
        # Check if configuration is complete
        if not email_service.is_configured():
            print("\n❌ OAuth configuration is incomplete!")
            print("Please set the following environment variables:")
            print("  - OAUTH_CLIENT_ID")
            print("  - OAUTH_CLIENT_SECRET")
            print("  - OAUTH_REFRESH_TOKEN")
            print("  - FROM_EMAIL")
            print("\nRun 'python scripts/setup_email.py' to configure OAuth settings.")
            return False
        
        print("\n🔗 Testing OAuth Connection...")
        
        # Test connection
        if email_service.test_connection():
            print("✅ OAuth connection successful!")
            
            # Test sending a sample email
            print("\n📤 Testing email sending...")
            test_email = input("Enter a test email address (or press Enter to skip): ").strip()
            
            if test_email:
                subject = "Job�co - OAuth Email Configuration Test"
                body = """
                <html>
                <body>
                    <h2>OAuth Email Configuration Test</h2>
                    <p>This is a test email to verify that your Job�co application OAuth configuration is working correctly.</p>
                    <p>If you received this email, your OAuth setup is successful!</p>
                    <p>This email was sent using OAuth 2.0 authentication, which is more secure than traditional passwords.</p>
                    <p>Best regards,<br>Job�co Team</p>
                </body>
                </html>
                """
                
                if email_service.send_group_invitation(test_email, "Test Group", "Test User", "test_token", "Never"):
                    print(f"✅ Test email sent successfully to {test_email}")
                    print("Please check your email inbox (and spam folder) for the test message.")
                else:
                    print("❌ Failed to send test email")
                    return False
            else:
                print("⏭️  Email sending test skipped")
            
            return True
        else:
            print("❌ OAuth connection failed!")
            print("\nPossible issues:")
            print("1. Invalid OAuth credentials")
            print("2. Expired refresh token")
            print("3. Gmail API not enabled")
            print("4. Network connectivity issues")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're running this script from the project root directory.")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Project root: {project_root}")
        print(f"Python path: {sys.path[:3]}...")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main function."""
    # Ensure we're in the right directory
    if not Path("main.py").exists():
        print("❌ Error: main.py not found!")
        print("Please run this script from the project root directory.")
        print(f"Current directory: {os.getcwd()}")
        return 1
    
    success = test_oauth_configuration()
    
    if success:
        print("\n🎉 OAuth configuration test completed successfully!")
        print("\nBenefits of OAuth:")
        print("✅ No passwords stored in your application")
        print("✅ More secure than app passwords")
        print("✅ Automatic token refresh")
        print("✅ Better audit trail")
        print("✅ Meets security compliance standards")
        print("\nNext steps:")
        print("1. Start your application: python main.py")
        print("2. Create a group and try sending an invitation")
        print("3. Check the application logs if you encounter any issues")
    else:
        print("\n💥 OAuth configuration test failed!")
        print("\nTroubleshooting:")
        print("1. Run 'python scripts/setup_email.py' to configure OAuth")
        print("2. Check the EMAIL_CONFIGURATION.md documentation")
        print("3. Verify your Google Cloud Project settings")
        print("4. Check the application logs for detailed error messages")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 
