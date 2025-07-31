# Email Configuration Setup Guide

This guide will help you set up OAuth-based email functionality for the Job�co application, specifically for sending group invitations.

## Quick Setup

1. **Copy the environment template:**
   ```bash
   cp docs/development.env.example .env
   ```

2. **Set up Google OAuth** (see detailed instructions below)

3. **Test the configuration** by running:
   ```bash
   python scripts/test_email.py
   ```

## Google OAuth Setup (Required)

The application uses Google OAuth 2.0 for secure email authentication. This is more secure than app passwords and provides better audit trails.

### Step 1: Create Google Cloud Project

1. **Go to Google Cloud Console:**
   - Visit [console.cloud.google.com](https://console.cloud.google.com)
   - Create a new project or select an existing one

2. **Enable Gmail API:**
   - Go to "APIs & Services" → "Library"
   - Search for "Gmail API"
   - Click "Enable"

### Step 2: Configure OAuth Consent Screen

1. **Go to OAuth consent screen:**
   - Navigate to "APIs & Services" → "OAuth consent screen"
   - Choose "External" user type
   - Fill in required information:
     - App name: "Job�co"
     - User support email: Your email
     - Developer contact information: Your email

2. **Add scopes:**
   - Click "Add or remove scopes"
   - Add these scopes:
     - `https://www.googleapis.com/auth/gmail.send`
     - `https://www.googleapis.com/auth/gmail.compose`

3. **Add test users** (for development):
   - Add your email address as a test user
   - This allows you to test the app before verification

### Step 3: Create OAuth Credentials

1. **Create OAuth 2.0 Client ID:**
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth 2.0 Client IDs"
   - Choose "Desktop application"
   - Name: "Job�co Desktop Client"

2. **Download credentials:**
   - Download the JSON file
   - Keep it secure (don't commit to version control)

### Step 4: Get Authorization Code

1. **Run the setup script:**
   ```bash
   python scripts/setup_email.py
   ```

2. **Follow the prompts:**
   - The script will open your browser
   - Authorize the application
   - Copy the authorization code from the browser
   - Paste it back into the terminal

3. **The script will:**
   - Exchange the authorization code for tokens
   - Update your `.env` file with the credentials
   - Test the configuration

## Environment Variables Explained

| Variable | Description | Example |
|----------|-------------|---------|
| `OAUTH_CLIENT_ID` | Google OAuth client ID | `123456789-abc123.apps.googleusercontent.com` |
| `OAUTH_CLIENT_SECRET` | Google OAuth client secret | `GOCSPX-abc123def456` |
| `OAUTH_REFRESH_TOKEN` | OAuth refresh token | `1//04abc123def456` |
| `FROM_EMAIL` | Sender email address | `user@gmail.com` |
| `APP_URL` | Your application's public URL | `https://yourdomain.com` |

## Complete .env File Example

```bash
# Job�co Application Environment Configuration

# Flask Environment
FLASK_ENV=development

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production

# Database Configuration
DATABASE=application.db

# Session Configuration
SESSION_FILE_DIR=flask_session

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# Application Settings
PASSWORD_MIN_LENGTH=6
MAX_LOGIN_ATTEMPTS=5
SESSION_TIMEOUT=3600

# Pagination Settings
DEFAULT_PAGE_SIZE=10
MAX_PAGE_SIZE=100

# CSRF Protection
WTF_CSRF_ENABLED=true
WTF_CSRF_TIME_LIMIT=3600

# OAuth Email Configuration (Required for group invitations)
OAUTH_CLIENT_ID=your-oauth-client-id
OAUTH_CLIENT_SECRET=your-oauth-client-secret
OAUTH_REFRESH_TOKEN=your-oauth-refresh-token
FROM_EMAIL=your-email@gmail.com
APP_URL=http://localhost:5000

# Development Settings
DEBUG=true
TESTING=false
```

## Testing Your Configuration

### Method 1: Command Line Test
```bash
python scripts/test_email.py
```

This will:
- Check your OAuth configuration
- Test the connection to Gmail API
- Send a test email (optional)

### Method 2: Web Interface
1. Start your application
2. Visit `http://localhost:5000/test_email_config`
3. Check if all configuration values are set correctly
4. Verify the connection test passes

### Method 3: Python Console
```python
from app.services.email_service import EmailService

# Test email service
email_service = EmailService()

# Check configuration
config_status = email_service.get_configuration_status()
print(f"OAuth Configured: {config_status['oauth_configured']}")
print(f"Client ID: {config_status['client_id']}")
print(f"Client Secret: {config_status['client_secret']}")
print(f"Refresh Token: {config_status['refresh_token']}")
print(f"From email: {config_status['from_email']}")
print(f"Access Token Valid: {config_status['access_token_valid']}")

# Test connection
if email_service.test_connection():
    print("✅ OAuth email configuration is working!")
else:
    print("❌ OAuth email configuration failed!")
```

## Troubleshooting

### Common Issues

1. **"Access blocked" error:**
   - Add your email as a test user in OAuth consent screen
   - For production, verify your app with Google

2. **"Invalid credentials" error:**
   - Check that your OAuth client ID and secret are correct
   - Verify the refresh token is valid
   - Re-run the setup script if needed

3. **"Token expired" error:**
   - The application automatically refreshes tokens
   - If this fails, re-run the setup script

4. **"Quota exceeded" error:**
   - Gmail API has daily quotas
   - Check your usage in Google Cloud Console

### OAuth Benefits

✅ **More Secure:** No passwords stored in your application  
✅ **Better Audit Trail:** All access is logged by Google  
✅ **Automatic Token Refresh:** Handled by the application  
✅ **Compliance:** Meets security standards for enterprise use  
✅ **No App Passwords:** Eliminates the need for app-specific passwords  

## Production Deployment

For production deployment:

1. **Verify your OAuth app** with Google (required for >100 users)
2. **Use environment variables** for all OAuth credentials
3. **Set up monitoring** for Gmail API quotas
4. **Configure proper logging** for email operations

## Security Best Practices

1. **Never commit OAuth credentials** to version control
2. **Use environment variables** for all sensitive data
3. **Rotate refresh tokens** periodically
4. **Monitor API usage** and set up alerts
5. **Use HTTPS** in production for all communications 
