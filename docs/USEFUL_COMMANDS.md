# Job�co Application - Useful Commands

This file contains useful commands for development, testing, and maintenance of the Job�co application.

## 🧪 Testing Commands

### Run All Tests
```bash
# Run complete test suite
python test_app.py

# Alternative using test runner
python run_tests.py
```

### Run Specific Service Tests
```bash
# Test database service only
python run_tests.py --service database

# Test user service only
python run_tests.py --service user

# Test group service only
python run_tests.py --service group

# Test tradesman service only
python run_tests.py --service tradesman

# Test job service only
python run_tests.py --service job

# Test integration scenarios only
python run_tests.py --service integration
```

### Test Options
```bash
# Quick tests (skip integration)
python run_tests.py --quick

# Verbose output
python run_tests.py --verbose

# Combine options
python run_tests.py --service user --verbose
```

## 🚀 Application Commands

### Start the Application
```bash
# Development mode
python app.py

# Production mode (if configured)
python app.py --production
```

### Database Management
```bash
# Initialize database
python sql/init_db.py

# Load sample data
python sql/load_db.py

# Read database contents
python sql/read_db.py
```

## 🔧 Development Commands

### Code Quality Checks
```bash
# Check for syntax errors
python -m py_compile app.py

# Check all Python files
find . -name "*.py" -exec python -m py_compile {} \;

# Run with Python debugger
python -m pdb app.py
```

### File Operations
```bash
# Find all Python files
find . -name "*.py"

# Find all template files
find . -name "*.html"

# Count lines of code
find . -name "*.py" -exec wc -l {} \;

# Search for specific text in files
grep -r "function_name" .
```

## 🗄️ Database Commands

### SQLite Operations
```bash
# Open database in SQLite CLI
sqlite3 application.db

# Backup database
sqlite3 application.db ".backup backup_$(date +%Y%m%d_%H%M%S).db"

# Export database schema
sqlite3 application.db ".schema" > schema_export.sql

# Export data
sqlite3 application.db ".dump" > data_export.sql

# Check database integrity
sqlite3 application.db "PRAGMA integrity_check;"
```

### Database Queries (SQLite CLI)
```sql
-- List all tables
.tables

-- Show table schema
.schema users
.schema groups
.schema tradesmen
.schema jobs

-- Count records in tables
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM groups;
SELECT COUNT(*) FROM tradesmen;
SELECT COUNT(*) FROM jobs;

-- View recent jobs
SELECT j.title, t.first_name, t.family_name, j.date_started 
FROM jobs j 
JOIN tradesmen t ON j.tradesman_id = t.id 
ORDER BY j.date_started DESC 
LIMIT 10;

-- View group memberships
SELECT g.name, u.username, ug.status 
FROM groups g 
JOIN user_groups ug ON g.id = ug.group_id 
JOIN users u ON ug.user_id = u.id;
```

## 🐛 Debugging Commands

### Log Analysis
```bash
# View application logs
tail -f logs/app.log

# Search logs for errors
grep "ERROR" logs/app.log

# Search logs for specific user
grep "username" logs/app.log

# View recent log entries
tail -n 50 logs/app.log
```

### Python Debugging
```bash
# Run with debug output
python -u app.py 2>&1 | tee debug.log

# Profile application
python -m cProfile -o profile.stats app.py

# Analyze profile results
python -c "import pstats; pstats.Stats('profile.stats').sort_stats('cumulative').print_stats(20)"
```

## 🔍 Search Commands

### Code Search
```bash
# Search for function definitions
grep -r "def " app/

# Search for route definitions
grep -r "@.*route" app/routes/

# Search for database queries
grep -r "execute_query" app/services/

# Search for template variables
grep -r "{{.*}}" templates/
```

### File Search
```bash
# Find files by name
find . -name "*service*"
find . -name "*route*"
find . -name "*template*"

# Find files by content
grep -l "UserService" app/routes/*.py
grep -l "create_user" app/services/*.py
```

## 🧹 Maintenance Commands

### Cleanup Operations
```bash
# Remove Python cache files
find . -type d -name "__pycache__" -exec rm -rf {} +

# Remove .pyc files
find . -name "*.pyc" -delete

# Clean temporary files
rm -f *.tmp *.log *.bak

# Remove test databases
rm -f test_*.db
```

### Backup Operations
```bash
# Create timestamped backup
cp application.db backup_$(date +%Y%m%d_%H%M%S).db

# Create backup directory
mkdir -p backups/$(date +%Y%m%d)
cp application.db backups/$(date +%Y%m%d)/

# Archive old backups
tar -czf backups_$(date +%Y%m).tar.gz backups/
```

## 📊 Monitoring Commands

### System Monitoring
```bash
# Check disk usage
du -sh .

# Check memory usage
ps aux | grep python

# Monitor file changes
watch -n 1 "ls -la logs/"

# Check open files
lsof | grep python
```

### Application Monitoring
```bash
# Check if app is running
ps aux | grep app.py

# Monitor log file growth
watch -n 5 "wc -l logs/app.log"

# Check database size
ls -lh application.db
```

## 🚀 Deployment Commands

### Production Setup
```bash
# Install production dependencies
pip install -r requirements.txt

# Set production environment
export FLASK_ENV=production
export SECRET_KEY="your-production-secret-key"

# Run with production server
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Development Setup
```bash
# Install development dependencies
pip install -r requirements.txt

# Set development environment
export FLASK_ENV=development
export FLASK_DEBUG=1

# Run development server
python app.py
```

## 🔧 Utility Scripts

### Quick Database Reset
```bash
# Create a script to reset database
cat > reset_db.sh << 'EOF'
#!/bin/bash
echo "Resetting database..."
rm -f application.db
python sql/init_db.py
python sql/load_db.py
echo "Database reset complete!"
EOF
chmod +x reset_db.sh
```

### Quick Test Run
```bash
# Create a script for quick testing
cat > quick_test.sh << 'EOF'
#!/bin/bash
echo "Running quick tests..."
python run_tests.py --quick --verbose
echo "Quick tests complete!"
EOF
chmod +x quick_test.sh
```

## 📝 Notes

- Always backup your database before running maintenance commands
- Test commands in a development environment first
- Monitor logs for any errors during operations
- Keep track of database changes and migrations
- Regular testing helps catch issues early

## 🆘 Emergency Commands

### If Application Won't Start
```bash
# Check for syntax errors
python -m py_compile app.py

# Check database integrity
sqlite3 application.db "PRAGMA integrity_check;"

# Check log files
tail -n 100 logs/app.log

# Reset database (CAUTION: loses data)
rm application.db && python sql/init_db.py
```

### If Tests Are Failing
```bash
# Run tests with maximum verbosity
python run_tests.py --verbose

# Check specific service
python run_tests.py --service database --verbose

# Check Python path
python -c "import sys; print(sys.path)"

# Check imports
python -c "from app.services.database import DatabaseService; print('Import OK')"
``` 
