# Production Commands Quick Reference

This document provides quick reference commands for managing the Fair Price application in production.

## Service Management

### Start/Stop/Restart Application
```bash
# Start the application service
sudo systemctl start fair-price.service

# Stop the application service
sudo systemctl stop fair-price.service

# Restart the application service
sudo systemctl restart fair-price.service

# Check service status
sudo systemctl status fair-price.service

# Enable service to start on boot
sudo systemctl enable fair-price.service

# Disable service from starting on boot
sudo systemctl disable fair-price.service
```

### Nginx Management
```bash
# Start Nginx
sudo systemctl start nginx

# Stop Nginx
sudo systemctl stop nginx

# Restart Nginx
sudo systemctl restart nginx

# Reload Nginx configuration
sudo systemctl reload nginx

# Check Nginx status
sudo systemctl status nginx

# Test Nginx configuration
sudo nginx -t
```

## Logs and Monitoring

### View Application Logs
```bash
# View application logs
sudo journalctl -u fair-price.service -f

# View recent application logs
sudo journalctl -u fair-price.service -n 100

# View logs since specific time
sudo journalctl -u fair-price.service --since "2024-01-01 00:00:00"

# View error logs only
sudo journalctl -u fair-price.service -p err
```

### View Nginx Logs
```bash
# View Nginx access logs
sudo tail -f /var/log/nginx/fair-price-access.log

# View Nginx error logs
sudo tail -f /var/log/nginx/fair-price-error.log

# View all Nginx logs
sudo tail -f /var/log/nginx/*.log
```

### View Application-Specific Logs
```bash
# View application log file
sudo tail -f /var/log/fair-price/app.log

# View backup logs
sudo tail -f /var/log/fair-price/backup.log
```

## Database Management

### Database Backup
```bash
# Manual database backup
sudo cp /var/lib/fair-price/production.db /var/backups/fair-price/db_backup_$(date +%Y%m%d_%H%M%S).db

# Run automated backup script
sudo -u www-data /var/www/fair-price/backup.sh

# List recent backups
ls -la /var/backups/fair-price/

# Restore database from backup
sudo cp /var/backups/fair-price/db_backup_YYYYMMDD_HHMMSS.db /var/lib/fair-price/production.db
sudo chown www-data:www-data /var/lib/fair-price/production.db
sudo chmod 640 /var/lib/fair-price/production.db
```

### Database Maintenance
```bash
# Connect to database for maintenance
sudo -u www-data sqlite3 /var/lib/fair-price/production.db

# Check database integrity
sudo -u www-data sqlite3 /var/lib/fair-price/production.db "PRAGMA integrity_check;"

# Optimize database
sudo -u www-data sqlite3 /var/lib/fair-price/production.db "VACUUM;"
```

## Configuration Management

### Environment Variables
```bash
# View current environment variables
sudo systemctl show fair-price.service --property=Environment

# Reload environment variables
sudo systemctl daemon-reload
sudo systemctl restart fair-price.service
```

### Update Configuration
```bash
# Update Nginx configuration
sudo nano /etc/nginx/sites-available/fair-price
sudo nginx -t
sudo systemctl reload nginx

# Update systemd service
sudo nano /etc/systemd/system/fair-price.service
sudo systemctl daemon-reload
sudo systemctl restart fair-price.service
```

## Application Updates

### Deploy New Version
```bash
# Stop application
sudo systemctl stop fair-price.service

# Backup current version
sudo cp -r /var/www/fair-price /var/www/fair-price.backup.$(date +%Y%m%d_%H%M%S)

# Update application code
cd /var/www/fair-price
sudo git pull origin main

# Update dependencies
sudo -u www-data /var/www/fair-price/.venv/bin/pip install -r requirements.txt

# Set proper permissions
sudo chown -R www-data:www-data /var/www/fair-price

# Start application
sudo systemctl start fair-price.service

# Check status
sudo systemctl status fair-price.service
```

### Rollback to Previous Version
```bash
# Stop application
sudo systemctl stop fair-price.service

# Restore previous version
sudo rm -rf /var/www/fair-price
sudo cp -r /var/www/fair-price.backup.YYYYMMDD_HHMMSS /var/www/fair-price

# Set proper permissions
sudo chown -R www-data:www-data /var/www/fair-price

# Start application
sudo systemctl start fair-price.service
```

## Health Checks

### Application Health
```bash
# Check if application is responding
curl -f http://127.0.0.1:8000/health

# Check application through Nginx
curl -f https://yourdomain.com/health

# Check application logs for errors
sudo journalctl -u fair-price.service -p err --since "1 hour ago"
```

### System Health
```bash
# Check disk space
df -h

# Check memory usage
free -h

# Check system load
uptime

# Check running processes
ps aux | grep fair-price
ps aux | grep nginx
```

## Security

### SSL Certificate Management
```bash
# Check SSL certificate expiration
openssl x509 -in /path/to/certificate.crt -text -noout | grep "Not After"

# Renew Let's Encrypt certificate
sudo certbot renew

# Test SSL configuration
openssl s_client -connect yourdomain.com:443 -servername yourdomain.com
```

### Firewall Management
```bash
# Check firewall status
sudo ufw status

# Allow HTTP and HTTPS
sudo ufw allow 80
sudo ufw allow 443

# Allow SSH (if needed)
sudo ufw allow ssh
```

## Troubleshooting

### Common Issues

#### Application Won't Start
```bash
# Check service status
sudo systemctl status fair-price.service

# Check logs for errors
sudo journalctl -u fair-price.service -p err

# Check file permissions
ls -la /var/www/fair-price/
ls -la /var/lib/fair-price/
ls -la /var/log/fair-price/
```

#### Database Issues
```bash
# Check database file permissions
ls -la /var/lib/fair-price/production.db

# Check database integrity
sudo -u www-data sqlite3 /var/lib/fair-price/production.db "PRAGMA integrity_check;"

# Check database size
du -h /var/lib/fair-price/production.db
```

#### Email Issues
```bash
# Test email configuration
sudo -u www-data /var/www/fair-price/.venv/bin/python -c "
from app.services.email_service import EmailService
email_service = EmailService()
print('Email test:', email_service.test_connection())
"
```

#### Nginx Issues
```bash
# Check Nginx configuration
sudo nginx -t

# Check Nginx error logs
sudo tail -f /var/log/nginx/error.log

# Check Nginx access logs
sudo tail -f /var/log/nginx/access.log
```

## Performance Monitoring

### Resource Usage
```bash
# Monitor CPU and memory usage
htop

# Monitor disk I/O
iotop

# Monitor network usage
iftop

# Monitor application performance
sudo journalctl -u fair-price.service --since "1 hour ago" | grep "response time"
```

### Database Performance
```bash
# Check database size
du -h /var/lib/fair-price/production.db

# Check database statistics
sudo -u www-data sqlite3 /var/lib/fair-price/production.db "PRAGMA stats;"

# Analyze database performance
sudo -u www-data sqlite3 /var/lib/fair-price/production.db "ANALYZE;"
```

## Maintenance Tasks

### Regular Maintenance
```bash
# Update system packages
sudo apt update && sudo apt upgrade

# Clean up old log files
sudo find /var/log -name "*.log.*" -mtime +30 -delete

# Clean up old backups
sudo find /var/backups/fair-price -name "db_backup_*.db" -mtime +7 -delete

# Optimize database
sudo -u www-data sqlite3 /var/lib/fair-price/production.db "VACUUM;"
```

### Emergency Procedures
```bash
# Emergency stop all services
sudo systemctl stop fair-price.service nginx

# Emergency restart
sudo systemctl restart fair-price.service nginx

# Emergency rollback
sudo systemctl stop fair-price.service
sudo cp /var/backups/fair-price/db_backup_LATEST.db /var/lib/fair-price/production.db
sudo systemctl start fair-price.service
``` 