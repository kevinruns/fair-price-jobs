#!/usr/bin/env python3
"""
Email Configuration Setup Script
This script helps you set up OAuth 2.0 email configuration for the Fair Price application.
"""

import os
import sys
import json
import webbrowser
from pathlib import Path
import requests
from urllib.parse import urlencode, parse_qs, urlparse

# Get the project root directory (parent of scripts directory)
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def get_user_input(prompt, default=None):
    """Get user input with optional default value."""
    if default:
        user_input = input(f"{prompt} [{default}]: ").strip()
        return user_input if user_input else default
    else:
        return input(f"{prompt}: ").strip()

def setup_google_oauth():
    """Guide user through Google OAuth setup."""
    print("\n=== Google OAuth Setup ===")
    print("This will set up OAuth 2.0 for Gmail API access.")
    print("You'll need to create a Google Cloud Project and enable the Gmail API.\n")
    
    # Step 1: Create Google Cloud Project
    print("Step 1: Create a Google Cloud Project")
    print("1. Go to https://console.cloud.google.com/")
    print("2. Create a new project or select an existing one")
    print("3. Enable the Gmail API:")
    print("   - Go to APIs & Services > Library")
    print("   - Search for 'Gmail API' and enable it")
    print("4. Create OAuth 2.0 credentials:")
    print("   - Go to APIs & Services > Credentials")
    print("   - Click 'Create Credentials' > 'OAuth 2.0 Client IDs'")
    print("   - Choose 'Desktop application' as application type")
    print("   - Download the JSON file\n")
    
    input("Press Enter when you've completed Step 1...")
    
    # Step 2: Get credentials
    print("\nStep 2: Enter OAuth Credentials")
    print("You can find these in the downloaded JSON file or in the Google Cloud Console.")
    
    client_id = get_user_input("Enter your OAuth Client ID")
    client_secret = get_user_input("Enter your OAuth Client Secret")
    
    if not client_id or not client_secret:
        print("❌ Client ID and Client Secret are required!")
        return None
    
    # Step 3: Get authorization code
    print("\nStep 3: Get Authorization Code")
    print("This will open your browser to authorize the application.")
    
    auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
    params = {
        'client_id': client_id,
        'redirect_uri': 'urn:ietf:wg:oauth:2.0:oob',
        'scope': 'https://www.googleapis.com/auth/gmail.send',
        'response_type': 'code',
        'access_type': 'offline',
        'prompt': 'consent'
    }
    
    auth_url_with_params = f"{auth_url}?{urlencode(params)}"
    
    print(f"Opening browser to: {auth_url_with_params}")
    try:
        webbrowser.open(auth_url_with_params)
    except:
        print("Please manually open this URL in your browser:")
        print(auth_url_with_params)
    
    print("\nAfter authorizing, you'll get an authorization code.")
    print("Copy and paste it below.")
    
    auth_code = get_user_input("Enter the authorization code")
    
    if not auth_code:
        print("❌ Authorization code is required!")
        return None
    
    # Step 4: Exchange for refresh token
    print("\nStep 4: Getting Refresh Token...")
    
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'code': auth_code,
        'grant_type': 'authorization_code',
        'redirect_uri': 'urn:ietf:wg:oauth:2.0:oob'
    }
    
    try:
        response = requests.post(token_url, data=data)
        response.raise_for_status()
        
        token_data = response.json()
        refresh_token = token_data.get('refresh_token')
        
        if not refresh_token:
            print("❌ No refresh token received!")
            print("This might happen if you've already authorized this application.")
            print("Try revoking access and trying again.")
            return None
        
        print("✅ Refresh token obtained successfully!")
        
        return {
            'OAUTH_CLIENT_ID': client_id,
            'OAUTH_CLIENT_SECRET': client_secret,
            'OAUTH_REFRESH_TOKEN': refresh_token
        }
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error getting refresh token: {e}")
        return None

def write_env_file(config, from_email, app_url):
    """Write OAuth configuration to .env file."""
    env_path = Path('.env')
    
    # Read existing .env file if it exists
    existing_lines = []
    if env_path.exists():
        with open(env_path, 'r') as f:
            existing_lines = f.readlines()
    
    # Update or add OAuth configuration
    new_lines = []
    oauth_vars_added = set()
    
    for line in existing_lines:
        if line.startswith(('OAUTH_', 'FROM_EMAIL', 'APP_URL')):
            # Skip existing OAuth config lines
            continue
        new_lines.append(line)
    
    # Add OAuth configuration
    new_lines.append('\n# OAuth Email Configuration\n')
    for key, value in config.items():
        new_lines.append(f'{key}={value}\n')
        oauth_vars_added.add(key)
    
    new_lines.append(f'FROM_EMAIL={from_email}\n')
    new_lines.append(f'APP_URL={app_url}\n')
    
    # Write back to .env file
    with open(env_path, 'w') as f:
        f.writelines(new_lines)
    
    print(f"\n✅ OAuth configuration written to {env_path}")
    print("Configuration added:")
    for key, value in config.items():
        print(f"  {key}={value}")
    print(f"  FROM_EMAIL={from_email}")
    print(f"  APP_URL={app_url}")

def test_oauth_configuration():
    """Test the OAuth configuration."""
    print("\n=== Testing OAuth Configuration ===")
    
    try:
        from app.services.email_service import EmailService
        
        oauth_service = EmailService()
        
        if oauth_service.test_connection():
            print("✅ OAuth configuration test successful!")
            return True
        else:
            print("❌ OAuth configuration test failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error testing OAuth configuration: {e}")
        return False

def main():
    """Main setup function."""
    print("Fair Price - OAuth Email Configuration Setup")
    print("=" * 50)
    
    # Check if .env file exists
    env_path = Path('.env')
    if not env_path.exists():
        print("⚠️  No .env file found. Creating one from template...")
        if Path('docs/production.env.example').exists():
            import shutil
            shutil.copy('docs/production.env.example', '.env')
            print("✅ Created .env file from template")
        else:
            print("❌ production.env.example not found. Please create a .env file manually.")
            return
    
    # Get OAuth configuration
    oauth_config = setup_google_oauth()
    if not oauth_config:
        print("❌ OAuth setup failed!")
        return
    
    # Get email and app URL
    print("\n=== Email Configuration ===")
    from_email = get_user_input("Enter the email address to send from (must match OAuth account)")
    app_url = get_user_input("Enter your application URL", "http://localhost:5000")
    
    # Write configuration
    write_env_file(oauth_config, from_email, app_url)
    
    # Test configuration
    print("\n=== Testing Configuration ===")
    if test_oauth_configuration():
        print("\n🎉 OAuth email configuration completed successfully!")
        print("\nBenefits of OAuth:")
        print("✅ No passwords stored in your application")
        print("✅ More secure than app passwords")
        print("✅ Automatic token refresh")
        print("✅ Better audit trail")
        print("✅ Meets security compliance standards")
        print("\nNext steps:")
        print("1. Restart your application to load the new configuration")
        print("2. Try sending a group invitation to test the email functionality")
        print("3. Check the application logs if you encounter any issues")
    else:
        print("\n❌ OAuth configuration test failed!")
        print("Please check your configuration and try again.")

if __name__ == "__main__":
    main() 