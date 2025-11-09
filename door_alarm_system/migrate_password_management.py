#!/usr/bin/env python3
"""
Database migration: Add password management fields for 21 CFR Part 11 compliance
"""
import sqlite3
import os

def migrate():
    """Add password reset and management fields to User table"""
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'alarm_system.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🔄 Starting password management migration (21 CFR Part 11 Compliance)...")
    print("=" * 70)
    
    try:
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user'")
        if not cursor.fetchone():
            print("❌ User table not found. Please create tables first.")
            return
        
        # Check existing columns
        cursor.execute("PRAGMA table_info(user)")
        existing_columns = [col[1] for col in cursor.fetchall()]
        
        migrations = []
        
        # Add password_reset_required column
        if 'password_reset_required' not in existing_columns:
            print("📝 Adding password_reset_required column...")
            cursor.execute("ALTER TABLE user ADD COLUMN password_reset_required BOOLEAN DEFAULT 0")
            migrations.append('password_reset_required')
        
        # Add password_reset_token column
        if 'password_reset_token' not in existing_columns:
            print("📝 Adding password_reset_token column...")
            cursor.execute("ALTER TABLE user ADD COLUMN password_reset_token VARCHAR(100)")
            migrations.append('password_reset_token')
        
        # Add password_reset_expires column
        if 'password_reset_expires' not in existing_columns:
            print("📝 Adding password_reset_expires column...")
            cursor.execute("ALTER TABLE user ADD COLUMN password_reset_expires DATETIME")
            migrations.append('password_reset_expires')
        
        # Add password_changed_at column
        if 'password_changed_at' not in existing_columns:
            print("📝 Adding password_changed_at column...")
            cursor.execute("ALTER TABLE user ADD COLUMN password_changed_at DATETIME")
            migrations.append('password_changed_at')
        
        if migrations:
            conn.commit()
            print("\n✅ Migration completed successfully!")
            print(f"   Added {len(migrations)} column(s): {', '.join(migrations)}")
        else:
            print("ℹ️  All columns already exist. No migration needed.")
        
        print("\n" + "=" * 70)
        print("✨ Password Management Features Now Available:")
        print("   • Admins can reset user passwords (generates temporary password)")
        print("   • Users forced to change password on next login")
        print("   • Temporary passwords expire after 24 hours")
        print("   • All password actions logged for 21 CFR Part 11 compliance")
        print("   • Admins CANNOT directly set user passwords (compliant)")
        print("\n📋 21 CFR Part 11 Compliance:")
        print("   ✅ §11.300(a) - Unique identification codes")
        print("   ✅ §11.300(b) - Passwords used only by genuine owners")
        print("   ✅ Password management procedures in place")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Migration failed: {e}")
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    migrate()
