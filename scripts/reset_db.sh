#!/bin/bash
# Database Reset Script for Job�co Application

echo "🔄 Resetting Job�co Application Database..."
echo "================================================"

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Backup existing database if it exists
if [ -f "application.db" ]; then
    echo "📦 Creating backup of existing database..."
    cp application.db "backup_$(date +%Y%m%d_%H%M%S).db"
    echo "✅ Backup created"
fi

# Remove existing database
echo "🗑️  Removing existing database..."
rm -f application.db

# Initialize new database
echo "🏗️  Initializing new database..."
python sql/init_db.py

if [ $? -eq 0 ]; then
    echo "✅ Database initialized successfully"
else
    echo "❌ Failed to initialize database"
    exit 1
fi

# Load sample data
echo "📊 Loading sample data..."
python sql/load_db.py

if [ $? -eq 0 ]; then
    echo "✅ Sample data loaded successfully"
else
    echo "❌ Failed to load sample data"
    exit 1
fi

echo ""
echo "🎉 Database reset complete!"
echo "📁 New database: application.db"
echo "📊 You can now start the application with: python app.py" 
