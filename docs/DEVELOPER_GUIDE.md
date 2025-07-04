# Fair Price Application - Developer Guide

Quick reference for developers working on the Fair Price application.

## 🚀 Getting Started

### First Time Setup
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Initialize database
python sql/init_db.py

# 3. Load sample data (optional)
python sql/load_db.py

# 4. Run tests to verify setup
python run_tests.py --quick
```

### Start Development
```bash
# Start the application
python app.py

# Access at: http://localhost:5000
```

## 🧪 Testing Workflow

### During Development
```bash
# Quick tests (fast feedback)
python run_tests.py --quick

# Test specific service
python run_tests.py --service user

# Full test suite (before commits)
python run_tests.py
```

### Before Commits
```bash
# 1. Run all tests
python run_tests.py

# 2. Check for syntax errors
python -m py_compile app.py

# 3. Clean up
cleanup.bat  # Windows
./cleanup.sh # Linux/Mac
```

## 🗄️ Database Management

### Reset Database (Development)
```bash
# Windows
reset_db.bat

# Linux/Mac
./reset_db.sh
```

### Backup Database (Production)
```bash
# Windows
backup_db.bat

# Linux/Mac
./backup_db.sh
```

### Manual Database Operations
```bash
# View database
sqlite3 application.db

# Export schema
sqlite3 application.db ".schema" > schema.sql

# Check integrity
sqlite3 application.db "PRAGMA integrity_check;"
```

## 🔧 Development Commands

### Code Quality
```bash
# Check syntax
python -m py_compile app.py

# Find all Python files
find . -name "*.py"

# Search for function
grep -r "function_name" app/
```

### Debugging
```bash
# View logs
tail -f logs/app.log

# Run with debug output
python -u app.py 2>&1 | tee debug.log

# Profile application
python -m cProfile -o profile.stats app.py
```

## 📁 Project Structure

```
fair-price/
├── app/                    # Main application
│   ├── routes/            # Route handlers
│   ├── services/          # Business logic
│   └── config.py          # Configuration
├── templates/             # HTML templates
├── static/               # CSS, JS, images
├── sql/                  # Database scripts
├── logs/                 # Application logs
├── test_app.py           # Test suite
├── run_tests.py          # Test runner
└── *.bat/*.sh           # Utility scripts
```

## 🔄 Common Workflows

### Adding New Feature
1. **Create feature branch**
2. **Write tests first**
   ```bash
   python run_tests.py --service [service_name]
   ```
3. **Implement feature**
4. **Test thoroughly**
   ```bash
   python run_tests.py
   ```
5. **Clean up**
   ```bash
   cleanup.bat  # or ./cleanup.sh
   ```

### Database Schema Changes
1. **Backup current database**
   ```bash
   backup_db.bat  # or ./backup_db.sh
   ```
2. **Update schema.sql**
3. **Reset database**
   ```bash
   reset_db.bat  # or ./reset_db.sh
   ```
4. **Update tests**
5. **Run full test suite**

### Debugging Issues
1. **Check logs**
   ```bash
   tail -f logs/app.log
   ```
2. **Run specific tests**
   ```bash
   python run_tests.py --service [service] --verbose
   ```
3. **Check database**
   ```bash
   sqlite3 application.db "PRAGMA integrity_check;"
   ```

## 🚨 Emergency Procedures

### Application Won't Start
```bash
# 1. Check syntax
python -m py_compile app.py

# 2. Check database
sqlite3 application.db "PRAGMA integrity_check;"

# 3. Reset database (CAUTION: loses data)
reset_db.bat  # or ./reset_db.sh
```

### Tests Failing
```bash
# 1. Check imports
python -c "from app.services.database import DatabaseService"

# 2. Run with verbose output
python run_tests.py --verbose

# 3. Check specific service
python run_tests.py --service database --verbose
```

## 📝 Best Practices

### Code Organization
- **Routes**: Handle HTTP requests only
- **Services**: Contain business logic
- **Templates**: Display data only
- **Tests**: Test services, not routes

### Database Operations
- **Always use service layer** for database operations
- **Never use direct database calls** in routes
- **Backup before schema changes**
- **Test database operations** thoroughly

### Testing
- **Write tests for new features**
- **Run tests before commits**
- **Use isolated test databases**
- **Test both success and failure cases**

## 🔍 Useful Queries

### Database Queries
```sql
-- View recent jobs
SELECT j.title, t.first_name, j.date_started 
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

### Log Analysis
```bash
# Find errors
grep "ERROR" logs/app.log

# Find specific user activity
grep "username" logs/app.log

# View recent activity
tail -n 50 logs/app.log
```

## 🎯 Quick Reference

| Task | Command |
|------|---------|
| Start app | `python app.py` |
| Quick test | `python run_tests.py --quick` |
| Full test | `python run_tests.py` |
| Reset DB | `reset_db.bat` / `./reset_db.sh` |
| Backup DB | `backup_db.bat` / `./backup_db.sh` |
| Cleanup | `cleanup.bat` / `./cleanup.sh` |
| View logs | `tail -f logs/app.log` |
| Check DB | `sqlite3 application.db` | 