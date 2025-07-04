#!/bin/bash
# Cleanup Script for Fair Price Application

echo "🧹 Cleanup Script for Fair Price Application"
echo "============================================"

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

echo "🗑️  Starting cleanup process..."

# Remove Python cache files
echo "📁 Removing Python cache files..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
echo "✅ Python cache files removed"

# Remove .pyc files
echo "🐍 Removing .pyc files..."
find . -name "*.pyc" -delete 2>/dev/null
echo "✅ .pyc files removed"

# Remove temporary files
echo "📄 Removing temporary files..."
rm -f *.tmp *.log *.bak 2>/dev/null
echo "✅ Temporary files removed"

# Remove test databases
echo "🧪 Removing test databases..."
rm -f test_*.db 2>/dev/null
echo "✅ Test databases removed"

# Clean up old log files (keep last 5)
echo "📋 Cleaning up old log files..."
if [ -d "logs" ]; then
    cd logs
    ls -t *.log | tail -n +6 | xargs -r rm -f
    cd - > /dev/null
    echo "✅ Old log files cleaned up"
fi

# Show disk usage before and after
echo ""
echo "📊 Disk usage summary:"
echo "======================"
echo "Current directory size:"
du -sh . 2>/dev/null

echo ""
echo "🎉 Cleanup complete!"
echo ""
echo "📝 What was cleaned:"
echo "   - Python cache directories (__pycache__)"
echo "   - Compiled Python files (.pyc)"
echo "   - Temporary files (.tmp, .log, .bak)"
echo "   - Test databases (test_*.db)"
echo "   - Old log files (kept last 5)"
echo ""
echo "💡 Next steps:"
echo "   - Run tests: python run_tests.py"
echo "   - Start application: python app.py" 