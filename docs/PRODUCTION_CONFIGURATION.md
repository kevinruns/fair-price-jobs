# Production Configuration Guide

This guide covers the essential configuration steps for deploying the Fair Price application in a production environment.

## Environment Variables

Create a `.env` file in your production environment with the following variables:

```bash
# Flask Environment
FLASK_ENV=production

# Security (CHANGE THESE IN PRODUCTION!)
SECRET_KEY=your-super-secret-production-key-minimum-32-characters

# Database Configuration
DATABASE=production.db

# Session Configuration
SESSION_FILE_DIR=/var/lib/fair-price/sessions
SESSION_PERMANENT=true
SESSION_TIMEOUT=86400

# Logging Configuration
LOG_LEVEL=WARNING
LOG_FILE=/var/log/fair-price/app.log

# Application Settings
PASSWORD_MIN_LENGTH=8
MAX_LOGIN_ATTEMPTS=3
SESSION_TIMEOUT=86400

# Pagination Settings
DEFAULT_PAGE_SIZE=20
MAX_PAGE_SIZE=100

# CSRF Protection
WTF_CSRF_ENABLED=true
WTF_CSRF_TIME_LIMIT=3600

# OAuth Email Configuration (Required for group invitations)
OAUTH_CLIENT_ID=your-oauth-client-id
OAUTH_CLIENT_SECRET=your-oauth-client-secret
OAUTH_REFRESH_TOKEN=your-oauth-refresh-token
FROM_EMAIL=your-production-email@gmail.com
APP_URL=https://yourdomain.com

# Production Settings
DEBUG=false
TESTING=false
```

## OAuth Email Setup

### 1. OAuth Configuration
The application requires OAuth 2.0 configuration for group invitation emails:

```bash
OAUTH_CLIENT_ID=your-oauth-client-id
OAUTH_CLIENT_SECRET=your-oauth-client-secret
OAUTH_REFRESH_TOKEN=your-oauth-refresh-token
FROM_EMAIL=your-production-email@gmail.com
APP_URL=https://yourdomain.com
```

**Setup Steps:**
1. Create a Google Cloud Project
2. Enable Gmail API
3. Configure OAuth consent screen
4. Create OAuth 2.0 credentials
5. Use the setup script: `python scripts/setup_email.py`

**Security Notes:**
1. Use a dedicated production email account
2. Keep OAuth credentials secure
3. Monitor Gmail API quotas
4. Set up proper logging for email operations

## Database Setup

### 1. Initialize Database
```bash
python sql/init_db.py
```

### 2. Database Permissions
Ensure the application has read/write permissions to the database file and directory.

### 3. Database Backup
Set up regular backups of your production database.

## Web Server Configuration

### Nginx Configuration Example
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /path/to/your/certificate.crt;
    ssl_certificate_key /path/to/your/private.key;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /path/to/your/app/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### Gunicorn Configuration
Create a `gunicorn.conf.py` file:

```python
bind = "127.0.0.1:5000"
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True
```

## Security Considerations

### 1. HTTPS
- Always use HTTPS in production
- Redirect HTTP to HTTPS
- Use strong SSL/TLS configuration

### 2. Secret Key
- Generate a strong, random secret key
- Never commit the secret key to version control
- Use environment variables for all secrets

### 3. File Permissions
```bash
# Set proper file permissions
chmod 600 .env
chmod 644 production.db
chmod 755 /var/log/fair-price
```

### 4. Firewall Configuration
```bash
# Allow only necessary ports
ufw allow 22    # SSH
ufw allow 80    # HTTP (redirect to HTTPS)
ufw allow 443   # HTTPS
ufw enable
```

## Monitoring and Logging

### 1. Application Logs
Configure log rotation:
```bash
# /etc/logrotate.d/fair-price
/var/log/fair-price/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
}
```

### 2. System Monitoring
Set up monitoring for:
- Application uptime
- Database performance
- Disk space usage
- Memory usage
- Gmail API quotas

### 3. Error Tracking
Consider implementing error tracking services like Sentry for production monitoring.

## Deployment Checklist

- [ ] Environment variables configured
- [ ] OAuth email setup completed
- [ ] Database initialized
- [ ] SSL certificate installed
- [ ] Web server configured
- [ ] Firewall configured
- [ ] Logging configured
- [ ] Monitoring set up
- [ ] Backup strategy implemented
- [ ] Security measures in place

## Troubleshooting

### Common Production Issues

1. **Email sending fails:**
   - Check OAuth configuration
   - Verify Gmail API quotas
   - Check application logs

2. **Database errors:**
   - Verify file permissions
   - Check disk space
   - Review database logs

3. **Performance issues:**
   - Monitor resource usage
   - Check database queries
   - Review application logs

4. **Security issues:**
   - Verify HTTPS configuration
   - Check file permissions
   - Review access logs 