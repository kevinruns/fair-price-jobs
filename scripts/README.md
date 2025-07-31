# Job�co Application - Utility Scripts

This folder contains utility scripts for the Job�co application. These scripts automate common development and maintenance tasks.

## 🚀 **Quick Start**

### Windows Users
```cmd
# Reset database
scripts\reset_db.bat

# Run quick tests
scripts\quick_test.bat

# Backup database
scripts\backup_db.bat

# Clean up files
scripts\cleanup.bat
```

### Linux/Mac Users
```bash
# Make scripts executable (first time only)
chmod +x scripts/*.sh

# Reset database
./scripts/reset_db.sh

# Run quick tests
./scripts/quick_test.sh

# Backup database
./scripts/backup_db.sh

# Clean up files
./scripts/cleanup.sh
```

## 📋 **Script Overview**

### **Database Management**
| Script | Purpose | When to Use |
|--------|---------|-------------|
| `reset_db.bat/.sh` | Reset database with backup | Development, testing |
| `backup_db.bat/.sh` | Create timestamped backup | Before changes, production |

### **Testing**
| Script | Purpose | When to Use |
|--------|---------|-------------|
| `quick_test.bat/.sh` | Run basic tests | During development |
| `tests/test_app.py` | Run full test suite | Before commits |

### **Maintenance**
| Script | Purpose | When to Use |
|--------|---------|-------------|
| `cleanup.bat/.sh` | Remove temporary files | Regular maintenance |

## 🔧 **Script Details**

### **reset_db.bat/.sh**
- **Purpose**: Reset database to clean state
- **Actions**:
  - Creates backup of existing database
  - Removes current database
  - Initializes new database
  - Loads sample data
- **Use when**: Starting development, testing schema changes

### **quick_test.bat/.sh**
- **Purpose**: Run basic tests quickly
- **Actions**:
  - Runs service tests (no integration)
  - Provides verbose output
  - Shows test summary
- **Use when**: During development, before commits

### **backup_db.bat/.sh**
- **Purpose**: Create database backup
- **Actions**:
  - Creates timestamped backup
  - Organizes backups by date
  - Cleans up old backups
- **Use when**: Before major changes, production maintenance

### **cleanup.bat/.sh**
- **Purpose**: Clean up temporary files
- **Actions**:
  - Removes Python cache files
  - Removes compiled Python files
  - Removes temporary files
  - Cleans old log files
- **Use when**: Regular maintenance, before commits

## 🛡️ **Safety Features**

### **Automatic Backups**
- Database reset scripts create backups automatically
- Backup scripts organize files by date
- Old backups are cleaned up automatically

### **Error Checking**
- All scripts check for required files
- Scripts validate directory structure
- Clear error messages for troubleshooting

### **Cross-Platform**
- Windows (.bat) and Unix (.sh) versions
- Same functionality across platforms
- Platform-specific optimizations

## 📝 **Usage Examples**

### **Development Workflow**
```bash
# 1. Start fresh
./scripts/reset_db.sh

# 2. Make changes to code
# ... edit files ...

# 3. Test changes
./scripts/quick_test.sh

# 4. Clean up before commit
./scripts/cleanup.sh
```

### **Production Maintenance**
```bash
# 1. Backup current database
./scripts/backup_db.sh

# 2. Make changes
# ... update application ...

# 3. Test thoroughly
python run_tests.py

# 4. Clean up
./scripts/cleanup.sh
```

## 🚨 **Troubleshooting**

### **Script Won't Run**
- Check if you're in the project root directory
- Ensure Python is installed and in PATH
- Verify required files exist

### **Permission Denied (Linux/Mac)**
```bash
chmod +x scripts/*.sh
```

### **Script Fails**
- Check error messages in output
- Verify database file exists
- Ensure Python dependencies are installed

## 📚 **Related Documentation**

- **[Developer Guide](../docs/DEVELOPER_GUIDE.md)** - Development workflow
- **[Useful Commands](../docs/USEFUL_COMMANDS.md)** - Manual commands
- **[Test Documentation](../docs/TEST_README.md)** - Testing guide

## 🔄 **Adding New Scripts**

When adding new utility scripts:

1. **Create both versions**: `.bat` for Windows, `.sh` for Unix
2. **Add safety checks**: Validate environment and files
3. **Include error handling**: Clear error messages
4. **Update this README**: Document purpose and usage
5. **Test on both platforms**: Ensure cross-platform compatibility 
