#!/bin/bash
# Database Backup Script for Job�co Application

echo "💾 Database Backup Script for Job�co Application"
echo "==================================================="

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Check if database exists
if [ ! -f "application.db" ]; then
    echo "❌ Error: application.db not found"
    exit 1
fi

# Create backup directory if it doesn't exist
BACKUP_DIR="backups/$(date +%Y%m%d)"
mkdir -p "$BACKUP_DIR"

# Create timestamped backup
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/application_$TIMESTAMP.db"

echo "📦 Creating backup..."
cp application.db "$BACKUP_FILE"

if [ $? -eq 0 ]; then
    echo "✅ Backup created successfully: $BACKUP_FILE"
    
    # Show backup file size
    BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    echo "📊 Backup size: $BACKUP_SIZE"
    
    # Show backup directory contents
    echo ""
    echo "📁 Backup directory contents:"
    ls -lh "$BACKUP_DIR"
    
    # Clean up old backups (keep last 10)
    echo ""
    echo "🧹 Cleaning up old backups (keeping last 10)..."
    cd "$BACKUP_DIR"
    ls -t | tail -n +11 | xargs -r rm -f
    cd - > /dev/null
    
    echo "✅ Backup process complete!"
else
    echo "❌ Failed to create backup"
    exit 1
fi

echo ""
echo "📝 Backup information:"
echo "   - Location: $BACKUP_FILE"
echo "   - Size: $BACKUP_SIZE"
echo "   - Date: $(date)"
echo ""
echo "💡 To restore from backup:"
echo "   cp $BACKUP_FILE application.db" 
