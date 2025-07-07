# Email Configuration Guide

This guide provides detailed information about setting up email functionality for the Fair Price application, specifically for group invitations.

## Overview

The Fair Price application uses email to send group invitations to users. The email system uses **OAuth 2.0** for secure, modern authentication with Gmail API.

## Why OAuth 2.0?

OAuth 2.0 is the **only authentication method** supported by Fair Price for several important reasons:

### **Security Benefits**

1. **No Password Storage** 🔒
   - No credentials stored in your application
   - Uses secure tokens that can be revoked independently
   - No risk of password exposure

2. **Scoped Permissions** 🎯
   - Only `gmail.send` permission granted
   - Cannot access other parts of your Google account
   - Minimal security footprint

3. **Revocable Access** 🔄
   - Tokens can be revoked without affecting your main account
   - Can revoke access from Google Cloud Console
   - Independent of other services

4. **Audit Trail** 📊
   - Google provides detailed access logs
   - Can see when and how your application accessed Gmail
   - Better compliance for production applications

### **User Experience Benefits**

1. **No 2FA Setup Required** ✅
   - Works with regular Google accounts
   - No need to enable 2-Factor Authentication
   - Simpler setup process

2. **No App Password Generation** 🚀
   - No need to navigate Google Account settings
   - No need to generate and manage 16-character passwords
   - Streamlined setup process

3. **Automatic Token Refresh** 🔄
   - OAuth handles token expiration automatically
   - No manual intervention required
   - More reliable long-term

### **Production Benefits**

1. **Compliance** 📋
   - Meets modern security standards
   - Better for enterprise deployments
   - Satisfies security audits

2. **Scalability** 📈
   - Better rate limits with OAuth
   - More reliable for high-volume applications
   - Google's preferred method

## Configuration Variables

The email system uses these environment variables (in `.env` file):

```bash
# OAuth Email Configuration
OAUTH_CLIENT_ID=your-oauth-client-id
OAUTH_CLIENT_SECRET=your-oauth-client-secret
OAUTH_REFRESH_TOKEN=your-refresh-token
FROM_EMAIL=your-email@gmail.com
APP_URL=https://yourdomain.com
```

## Setup Process

### **Automated Setup (Recommended)**

Use the provided setup script for easy OAuth configuration:

```bash
python scripts/setup_email.py
```

This interactive script guides you through:
1. **Google Cloud Project setup**
2. **Gmail API enablement**
3. **OAuth 2.0 credentials creation**
4. **Authorization flow**
5. **Refresh token generation**
6. **Configuration testing**

### **Step-by-Step OAuth Setup**

#### **Step 1: Create Google Cloud Project**
1. Go to https://console.cloud.google.com/
2. Create a new project or select an existing one
3. Enable the Gmail API:
   - Go to APIs & Services > Library
   - Search for 'Gmail API' and enable it

#### **Step 2: Create OAuth Credentials**
1. Go to APIs & Services > Credentials
2. Click 'Create Credentials' > 'OAuth 2.0 Client IDs'
3. Choose 'Desktop application' as application type
4. Download the JSON file or note the credentials

#### **Step 3: Run Setup Script**
```bash
python scripts/setup_email.py
```

#### **Step 4: Authorize Application**
1. Browser opens for authorization
2. Grant Gmail sending permissions
3. Copy authorization code
4. Script exchanges code for refresh token

#### **Step 5: Complete Setup**
1. Script updates `.env` file automatically
2. Tests configuration
3. Provides next steps

### **Manual Configuration**

1. **Create/Edit `.env` file**
   ```bash
   cp docs/production.env.example .env
   ```

2. **Add OAuth configuration**
   ```bash
   # OAuth Email Configuration
   OAUTH_CLIENT_ID=your-oauth-client-id
   OAUTH_CLIENT_SECRET=your-oauth-client-secret
   OAUTH_REFRESH_TOKEN=your-refresh-token
   FROM_EMAIL=your-email@gmail.com
   APP_URL=https://yourdomain.com
   ```

3. **Restart application**
   ```bash
   python main.py
   ```

## Testing Email Configuration

### **1. Automated Test Script**
```bash
python scripts/test_email.py
```

This script:
- Checks OAuth configuration completeness
- Tests Gmail API connection
- Optionally sends test email
- Provides detailed error messages

### **2. Web Interface Test**
Visit: `http://localhost:5000/test_email_config`

Shows:
- Configuration status
- Connection test results
- Missing settings

### **3. Integration Tests**
```bash
python run_tests.py --service email
```

Runs comprehensive email tests including:
- OAuth service functionality
- Invitation creation/sending
- Error handling
- Integration workflows

## Email Workflow

### **Group Invitation Process**
1. User creates/joins a group
2. User clicks "Send Invitation" 
3. System creates invitation record with secure token
4. Email sent via Gmail API with invitation link
5. Recipient clicks link to accept
6. User added to group automatically

### **Email Content**
Invitation emails include:
- Group name and description
- Inviter's name
- Secure invitation link
- Expiration date (7 days default)
- Application branding

## Security Features

### **OAuth Token Management**
- **32-character secure tokens** for invitations
- **Single-use only** - tokens expire after use
- **7-day expiration** by default
- **Stored securely** in database

### **Environment Variables**
- **Never commit `.env`** to version control
- **Use strong credentials** - unique OAuth client secrets
- **Rotate credentials** regularly if needed

### **Access Control**
- **Scoped permissions** - only email sending
- **Revocable access** - can be revoked anytime
- **Audit logging** - Google provides access logs

## Troubleshooting

### **Common Issues & Solutions**

#### **1. "OAuth not properly configured"**
- Check all OAuth variables are set in `.env`
- Ensure no extra spaces or quotes around values
- Restart application after making changes

#### **2. "Failed to refresh OAuth token"**
- Refresh token may have expired
- Re-run setup: `python scripts/setup_email.py`
- Check Google Cloud Console for token status

#### **3. "Gmail API quota exceeded"**
- Check Gmail API quotas in Google Cloud Console
- Consider upgrading to paid plan for higher limits
- Monitor usage in Google Cloud Console

#### **4. "Invalid OAuth credentials"**
- Verify client ID and secret are correct
- Check that Gmail API is enabled
- Ensure credentials are for desktop application

#### **5. "Emails not being received"**
- Check spam/junk folder
- Verify sender email address is correct
- Check Gmail API sending limits

### **Debug Mode**

Enable debug logging for detailed OAuth information:

```bash
LOG_LEVEL=DEBUG
```

This will show detailed Gmail API communication in the logs.

## Production Deployment

### **1. Google Cloud Project Setup**
```bash
# Use production project
# Enable Gmail API
# Create OAuth 2.0 credentials
# Set authorized redirect URIs
```

### **2. Environment Variables**
```bash
export OAUTH_CLIENT_ID=your-production-client-id
export OAUTH_CLIENT_SECRET=your-production-client-secret
export OAUTH_REFRESH_TOKEN=your-production-refresh-token
export FROM_EMAIL=your-production-email@gmail.com
export APP_URL=https://yourdomain.com
```

### **3. Security Best Practices**
- Use dedicated Google account for application
- Enable audit logging in Google Cloud Console
- Monitor API usage and set up alerts
- Regular security reviews

### **4. Monitoring & Alerts**
- Monitor Gmail API quotas
- Set up usage alerts in Google Cloud Console
- Track email delivery rates
- Monitor application logs

## Files & Documentation

### **Key Files**
- `app/services/email_service.py` - OAuth email service
- `app/services/invitation_service.py` - Invitation management
- `scripts/setup_email.py` - OAuth setup script
- `scripts/test_email.py` - OAuth testing script
- `templates/send_invitation.html` - Invitation form

### **Configuration Files**
- `config.py` - Application configuration
- `.env` - Environment variables
- `docs/production.env.example` - Environment template

### **Test Files**
- `tests/test_email.py` - Comprehensive email tests
- `run_tests.py` - Test runner with email support

## Quick Start Commands

### **Setup & Testing**
```bash
# Setup OAuth configuration
python scripts/setup_email.py

# Test OAuth configuration
python scripts/test_email.py

# Run email tests
python run_tests.py --service email
```

### **Testing**
```bash
# Test in web interface
# Visit: http://localhost:5000/test_email_config

# Check application logs
tail -f logs/app.log | grep -i email
```

## Support

If you encounter issues:

1. **Check troubleshooting section** above
2. **Review application logs** for error messages
3. **Test with provided scripts** to isolate issues
4. **Verify Google Cloud Project settings**
5. **Check Gmail API quotas and status**
6. **Contact support** if needed

## Benefits Summary

### **Security**
- ✅ No password storage
- ✅ Scoped permissions
- ✅ Revocable access
- ✅ Audit trail
- ✅ Compliance ready

### **Simplicity**
- ✅ One authentication method
- ✅ One setup script
- ✅ Clear documentation
- ✅ Automated testing

### **Reliability**
- ✅ Automatic token refresh
- ✅ Google's preferred method
- ✅ Better rate limits
- ✅ Production ready

## Conclusion

OAuth 2.0 provides the most secure, reliable, and modern approach to email authentication for the Fair Price application. The simplified OAuth-only approach ensures consistent security standards, easier maintenance, and better user experience across all deployments. 