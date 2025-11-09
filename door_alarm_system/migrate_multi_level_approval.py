#!/usr/bin/env python3
"""
Migration script to add multi-level approval fields to ChangeControl and User tables
"""
import sqlite3
from datetime import datetime

DB_PATH = 'alarm_system.db'

def migrate():
    """Migrate database to support multi-level approval workflow"""
    import sqlite3
    import os
    
    # Use the correct database path
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'alarm_system.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🔄 Starting multi-level approval migration...")
    print("=" * 60)
    
    try:
        # Check if tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"\n📋 Found tables: {', '.join(tables)}")
        
        if not tables:
            print("\n⚠️  Database appears to be empty. Tables will be created on first app run.")
            print("✨ Please restart the Flask app to create tables, then run this migration again.")
            return
        
        # Add approval_level to User table
        print("\n📝 Adding approval_level to User table...")
        try:
            cursor.execute("ALTER TABLE user ADD COLUMN approval_level VARCHAR(20) DEFAULT 'user'")
            print("✅ Added approval_level column to User table")
        except sqlite3.OperationalError as e:
            if 'duplicate column name' in str(e).lower():
                print("ℹ️  approval_level column already exists in User table")
            else:
                raise
        
        # Update existing users
        print("\n📝 Setting approval levels for existing users...")
        cursor.execute("UPDATE user SET approval_level = 'admin' WHERE is_admin = 1")
        cursor.execute("UPDATE user SET approval_level = 'user' WHERE is_admin = 0 OR is_admin IS NULL")
        print("✅ Updated existing user approval levels")
        
        # Add supervisor approval fields to ChangeControl
        print("\n📝 Adding supervisor approval fields to ChangeControl table...")
        fields_to_add = [
            ("supervisor_approved_by", "INTEGER"),
            ("supervisor_approved_date", "DATETIME"),
            ("supervisor_signature_id", "INTEGER"),
            ("manager_approved_by", "INTEGER"),
            ("manager_approved_date", "DATETIME"),
            ("manager_signature_id", "INTEGER"),
            ("director_approved_by", "INTEGER"),
            ("director_approved_date", "DATETIME"),
            ("director_signature_id", "INTEGER"),
        ]
        
        for field_name, field_type in fields_to_add:
            try:
                cursor.execute(f"ALTER TABLE change_control ADD COLUMN {field_name} {field_type}")
                print(f"✅ Added {field_name} to ChangeControl table")
            except sqlite3.OperationalError as e:
                if 'duplicate column name' in str(e).lower():
                    print(f"ℹ️  {field_name} already exists")
                else:
                    raise
        
        # Update status column to support new status values
        print("\n📝 Migrating existing change request statuses...")
        
        # Get existing change requests
        cursor.execute("SELECT id, status FROM change_control")
        changes = cursor.fetchall()
        
        for change_id, old_status in changes:
            if old_status == 'pending':
                new_status = 'pending_supervisor'
            elif old_status in ['approved', 'rejected', 'implemented']:
                new_status = old_status
            else:
                new_status = 'pending_supervisor'
            
            cursor.execute("UPDATE change_control SET status = ? WHERE id = ?", (new_status, change_id))
            print(f"  Updated change {change_id}: '{old_status}' → '{new_status}'")
        
        conn.commit()
        print("\n" + "=" * 60)
        print("✨ Migration completed successfully!")
        print("\nNew approval workflow:")
        print("  1. User creates request → Status: pending_supervisor")
        print("  2. Supervisor approves → Status: pending_manager")
        print("  3. Manager approves → Status: pending_director")
        print("  4. Director approves → Status: pending_admin")
        print("  5. Admin approves → Status: approved")
        print("  6. Admin implements → Status: implemented")
        print("\nUser approval levels: user, supervisor, manager, director, admin")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Migration failed: {str(e)}")
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    migrate()
