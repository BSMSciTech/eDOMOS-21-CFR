#!/usr/bin/env python3
"""
Database migration script to add UserPreference table
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import UserPreference

def migrate_database():
    """Add UserPreference table to database"""
    with app.app_context():
        print("🔄 Starting database migration...")
        print("📋 Adding UserPreference table...")
        
        try:
            # Create UserPreference table
            db.create_all()
            
            print("✅ UserPreference table created successfully!")
            print("✨ Database migration complete!")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        return True

if __name__ == '__main__':
    success = migrate_database()
    sys.exit(0 if success else 1)
