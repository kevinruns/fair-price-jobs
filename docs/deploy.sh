#!/bin/bash

# Jobéco Application - Production Deployment Script
# This script automates the deployment process for production environments
# Modify the variables below according to your environment

set -e  # Exit on any error

# =============================================================================
# CONFIGURATION VARIABLES - MODIFY THESE FOR YOUR ENVIRONMENT
# =============================================================================

# Application details
APP_NAME="fair-price"
APP_USER="www-data"
APP_GROUP="www-data"
APP_DIR="/var/www/fair-price"
VENV_DIR="$APP_DIR/.venv"

# Database configuration
DB_DIR="/var/lib/fair-price"
DB_FILE="$DB_DIR/production.db"

# Session configuration
SESSION_DIR="/var/lib/fair-price/sessions"

# Logging configuration
LOG_DIR="/var/log/fair-price"

# Backup configuration
BACKUP_DIR="/var/backups/fair-price"

# Web server configuration
NGINX_CONF="/etc/nginx/sites-available/fair-price"
NGINX_ENABLED="/etc/nginx/sites-enabled/fair-price"
SYSTEMD_SERVICE="/etc/systemd/system/fair-price.service"

# =============================================================================
# COLOR OUTPUT FUNCTIONS
# =============================================================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_error "This script must be run as root"
        exit 1
    fi
}

create_directory() {
    local dir="$1"
    local owner="$2"
    local perms="$3"
    
    if [[ ! -d "$dir" ]]; then
        print_info "Creating directory: $dir"
        mkdir -p "$dir"
    fi
    
    if [[ -n "$owner" ]]; then
        chown "$owner" "$dir"
    fi
    
    if [[ -n "$perms" ]]; then
        chmod "$perms" "$dir"
    fi
}

backup_database() {
    if [[ -f "$DB_FILE" ]]; then
        local backup_file="$BACKUP_DIR/db_backup_$(date +%Y%m%d_%H%M%S).db"
        print_info "Creating database backup: $backup_file"
        cp "$DB_FILE" "$backup_file"
        print_success "Database backed up to: $backup_file"
    else
        print_warning "No existing database found to backup"
    fi
}

# =============================================================================
# MAIN DEPLOYMENT FUNCTIONS
# =============================================================================

setup_directories() {
    print_info "Setting up application directories..."
    
    create_directory "$APP_DIR" "$APP_USER:$APP_GROUP" "755"
    create_directory "$DB_DIR" "$APP_USER:$APP_GROUP" "750"
    create_directory "$SESSION_DIR" "$APP_USER:$APP_GROUP" "750"
    create_directory "$LOG_DIR" "$APP_USER:$APP_GROUP" "750"
    create_directory "$BACKUP_DIR" "$APP_USER:$APP_GROUP" "750"
    
    print_success "Directories created successfully"
}

setup_python_environment() {
    print_info "Setting up Python virtual environment..."
    
    if [[ ! -d "$VENV_DIR" ]]; then
        python3 -m venv "$VENV_DIR"
    fi
    
    # Activate virtual environment and install dependencies
    source "$VENV_DIR/bin/activate"
    pip install --upgrade pip
    pip install -r "$APP_DIR/requirements.txt"
    
    print_success "Python environment setup complete"
}

setup_database() {
    print_info "Setting up database..."
    
    # Backup existing database
    backup_database
    
    # Initialize database if it doesn't exist
    if [[ ! -f "$DB_FILE" ]]; then
        print_info "Initializing new database..."
        cd "$APP_DIR"
        source "$VENV_DIR/bin/activate"
        python sql/init_db.py
        print_success "Database initialized"
    else
        print_info "Using existing database"
    fi
    
    # Set proper permissions
    chown "$APP_USER:$APP_GROUP" "$DB_FILE"
    chmod 640 "$DB_FILE"
}

create_systemd_service() {
    print_info "Creating systemd service..."
    
    cat > "$SYSTEMD_SERVICE" << EOF
[Unit]
Description=Jobéco Application
After=network.target

[Service]
User=$APP_USER
Group=$APP_GROUP
WorkingDirectory=$APP_DIR
Environment="PATH=$VENV_DIR/bin"
Environment="FLASK_ENV=production"
ExecStart=$VENV_DIR/bin/gunicorn -w 4 -b 127.0.0.1:8000 main:app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    systemctl enable fair-price.service
    
    print_success "Systemd service created and enabled"
}

setup_nginx() {
    print_info "Setting up Nginx configuration..."
    
    # Create Nginx configuration
    cat > "$NGINX_CONF" << EOF
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    # SSL Configuration - Update these paths
    ssl_certificate /path/to/your/certificate.crt;
    ssl_certificate_key /path/to/your/private.key;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Proxy to application
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }

    # Static files
    location /static {
        alias $APP_DIR/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
        add_header X-Content-Type-Options nosniff;
    }

    # Logs
    access_log /var/log/nginx/fair-price-access.log;
    error_log /var/log/nginx/fair-price-error.log;
}
EOF

    # Enable site
    ln -sf "$NGINX_CONF" "$NGINX_ENABLED"
    
    # Test Nginx configuration
    nginx -t
    
    print_success "Nginx configuration created"
}

setup_log_rotation() {
    print_info "Setting up log rotation..."
    
    cat > "/etc/logrotate.d/fair-price" << EOF
$LOG_DIR/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 640 $APP_USER $APP_GROUP
    postrotate
        systemctl reload fair-price.service
    endscript
}
EOF

    print_success "Log rotation configured"
}

setup_backup_cron() {
    print_info "Setting up automated backups..."
    
    # Create backup script
    cat > "$APP_DIR/backup.sh" << EOF
#!/bin/bash
# Automated backup script for Jobéco application

BACKUP_DIR="$BACKUP_DIR"
DB_FILE="$DB_FILE"
DATE=\$(date +%Y%m%d_%H%M%S)

# Create backup
cp "\$DB_FILE" "\$BACKUP_DIR/db_backup_\$DATE.db"

# Keep only last 7 days of backups
find \$BACKUP_DIR -name "db_backup_*.db" -mtime +7 -delete

# Log backup
echo "\$(date): Database backup completed" >> "$LOG_DIR/backup.log"
EOF

    chmod +x "$APP_DIR/backup.sh"
    chown "$APP_USER:$APP_GROUP" "$APP_DIR/backup.sh"
    
    # Add to crontab (daily at 2 AM)
    (crontab -u "$APP_USER" -l 2>/dev/null; echo "0 2 * * * $APP_DIR/backup.sh") | crontab -u "$APP_USER" -
    
    print_success "Automated backups configured"
}

verify_deployment() {
    print_info "Verifying deployment..."
    
    # Check if service is running
    if systemctl is-active --quiet fair-price.service; then
        print_success "Application service is running"
    else
        print_error "Application service is not running"
        systemctl status fair-price.service
        return 1
    fi
    
    # Check if Nginx is running
    if systemctl is-active --quiet nginx; then
        print_success "Nginx is running"
    else
        print_error "Nginx is not running"
        return 1
    fi
    
    # Test application health (if health endpoint exists)
    if curl -f -s http://127.0.0.1:8000/health > /dev/null 2>&1; then
        print_success "Application health check passed"
    else
        print_warning "Application health check failed (endpoint may not exist)"
    fi
    
    print_success "Deployment verification complete"
}

# =============================================================================
# MAIN SCRIPT
# =============================================================================

main() {
    print_info "Starting Jobéco application deployment..."
    
    # Check if running as root
    check_root
    
    # Run deployment steps
    setup_directories
    setup_python_environment
    setup_database
    create_systemd_service
    setup_nginx
    setup_log_rotation
    setup_backup_cron
    
    # Start services
    print_info "Starting services..."
    systemctl start fair-price.service
    systemctl reload nginx
    
    # Verify deployment
    verify_deployment
    
    print_success "Deployment completed successfully!"
    print_info "Next steps:"
    print_info "1. Update SSL certificate paths in Nginx configuration"
    print_info "2. Configure your domain name in Nginx configuration"
    print_info "3. Set up your .env file with production values"
    print_info "4. Test the application thoroughly"
    print_info "5. Monitor logs for any issues"
}

# Run main function
main "$@" 
