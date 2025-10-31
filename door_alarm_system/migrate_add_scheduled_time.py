#!/usr/bin/env python3
"""
Database migration script to add scheduled_time column to scheduled_report table
"""

import sqlite3
import os

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), 'instance', 'alarm_system.db')

def migrate():
    """Add scheduled_time column to scheduled_report table"""
    
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at: {DB_PATH}")
        return False
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if column already exists
        cursor.execute("PRAGMA table_info(scheduled_report)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'scheduled_time' in columns:
            print("✅ Column 'scheduled_time' already exists in scheduled_report table")
            conn.close()
            return True
        
        # Add the scheduled_time column with default value
        print("📝 Adding 'scheduled_time' column to scheduled_report table...")
        cursor.execute("""
            ALTER TABLE scheduled_report 
            ADD COLUMN scheduled_time VARCHAR(5) DEFAULT '09:00'
        """)
        
        conn.commit()
        
        # Verify the column was added
        cursor.execute("PRAGMA table_info(scheduled_report)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'scheduled_time' in columns:
            print("✅ Successfully added 'scheduled_time' column")
            
            # Show updated table structure
            print("\n📋 Updated table structure:")
            cursor.execute("PRAGMA table_info(scheduled_report)")
            for col in cursor.fetchall():
                print(f"   - {col[1]} ({col[2]})")
            
            # Update existing records to have default time
            cursor.execute("UPDATE scheduled_report SET scheduled_time = '09:00' WHERE scheduled_time IS NULL")
            conn.commit()
            updated = cursor.rowcount
            if updated > 0:
                print(f"\n✅ Updated {updated} existing record(s) with default time '09:00'")
            
            conn.close()
            return True
        else:
            print("❌ Failed to add column")
            conn.close()
            return False
            
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("🔧 DATABASE MIGRATION: Add scheduled_time column")
    print("=" * 60)
    print()
    
    success = migrate()
    
    print()
    print("=" * 60)
    if success:
        print("✅ MIGRATION COMPLETED SUCCESSFULLY")
        print("=" * 60)
        print()
        print("Next steps:")
        print("1. Restart the server: ./start.sh")
        print("2. Create new scheduled reports with time settings")
    else:
        print("❌ MIGRATION FAILED")
        print("=" * 60)
        print()
        print("Please check the error messages above and try again")
    print()
