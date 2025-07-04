#!/usr/bin/env python3
"""
Simple test script to verify the database service is working correctly.
"""

import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from app.services.database import get_db_service
from app.services.user_service import UserService
from app.services.tradesman_service import TradesmanService

def test_database_service():
    """Test the database service functionality."""
    print("Testing Database Service...")
    
    # Create application context
    with app.app_context():
        # Get the database service
        db_service = get_db_service()
        
        # Test basic database operations
        print("1. Testing database connection...")
        try:
            conn = db_service.get_connection()
            print("   ✓ Database connection successful")
        except Exception as e:
            print(f"   ✗ Database connection failed: {e}")
            return False
        
        # Test table existence
        print("2. Testing table existence...")
        tables = ['users', 'tradesmen', 'groups', 'jobs', 'user_groups', 'group_tradesmen', 'user_tradesmen']
        for table in tables:
            exists = db_service.table_exists(table)
            status = "✓" if exists else "✗"
            print(f"   {status} Table '{table}': {'exists' if exists else 'missing'}")
        
        # Test user service
        print("3. Testing User Service...")
        user_service = UserService()
        
        # Test getting users
        users = db_service.execute_query("SELECT COUNT(*) as count FROM users")
        user_count = users[0]['count'] if users else 0
        print(f"   ✓ Found {user_count} users in database")
        
        # Test tradesman service
        print("4. Testing Tradesman Service...")
        tradesman_service = TradesmanService()
        
        # Test getting tradesmen
        tradesmen = db_service.execute_query("SELECT COUNT(*) as count FROM tradesmen")
        tradesman_count = tradesmen[0]['count'] if tradesmen else 0
        print(f"   ✓ Found {tradesman_count} tradesmen in database")
        
        # Test search functionality
        print("5. Testing search functionality...")
        search_results = tradesman_service.search_tradesmen()
        print(f"   ✓ Search returned {len(search_results)} results")
        
        print("\nDatabase service test completed successfully!")
        return True

if __name__ == "__main__":
    success = test_database_service()
    sys.exit(0 if success else 1) 