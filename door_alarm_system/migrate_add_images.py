"""
Database Migration: Add camera image fields to EventLog table
Adds image_path, image_hash, and image_timestamp columns
"""

from app import app, db
from sqlalchemy import text
import sys

def check_columns_exist():
    """Check if image columns already exist"""
    with app.app_context():
        try:
            result = db.session.execute(text("PRAGMA table_info(event_log)"))
            columns = [row[1] for row in result]
            
            has_image_path = 'image_path' in columns
            has_image_hash = 'image_hash' in columns
            has_image_timestamp = 'image_timestamp' in columns
            
            return has_image_path, has_image_hash, has_image_timestamp
        except Exception as e:
            print(f"Error checking columns: {e}")
            return False, False, False

def migrate_add_image_columns():
    """Add image-related columns to EventLog table"""
    
    print("=" * 70)
    print("DATABASE MIGRATION: Add Camera Image Fields to EventLog")
    print("=" * 70)
    
    with app.app_context():
        try:
            # Check existing columns
            has_path, has_hash, has_timestamp = check_columns_exist()
            
            print("\n📋 Current Status:")
            print(f"   image_path column exists: {has_path}")
            print(f"   image_hash column exists: {has_hash}")
            print(f"   image_timestamp column exists: {has_timestamp}")
            
            if has_path and has_hash and has_timestamp:
                print("\n✅ All image columns already exist. No migration needed.")
                return True
            
            print("\n🔧 Starting migration...")
            
            # Add image_path column
            if not has_path:
                print("   Adding image_path column...")
                db.session.execute(text("""
                    ALTER TABLE event_log 
                    ADD COLUMN image_path VARCHAR(500)
                """))
                print("   ✅ image_path column added")
            
            # Add image_hash column
            if not has_hash:
                print("   Adding image_hash column...")
                db.session.execute(text("""
                    ALTER TABLE event_log 
                    ADD COLUMN image_hash VARCHAR(64)
                """))
                print("   ✅ image_hash column added")
            
            # Add image_timestamp column
            if not has_timestamp:
                print("   Adding image_timestamp column...")
                db.session.execute(text("""
                    ALTER TABLE event_log 
                    ADD COLUMN image_timestamp DATETIME
                """))
                print("   ✅ image_timestamp column added")
            
            # Commit changes
            db.session.commit()
            
            print("\n✅ Migration completed successfully!")
            
            # Verify migration
            print("\n🔍 Verifying migration...")
            result = db.session.execute(text("PRAGMA table_info(event_log)"))
            columns = [(row[1], row[2]) for row in result]
            
            print("\n📊 EventLog Table Schema:")
            for col_name, col_type in columns:
                marker = "🆕" if col_name in ['image_path', 'image_hash', 'image_timestamp'] else "  "
                print(f"   {marker} {col_name}: {col_type}")
            
            # Show sample query
            print("\n📝 Sample Query Test:")
            result = db.session.execute(text("""
                SELECT id, event_type, image_path, image_hash 
                FROM event_log 
                LIMIT 5
            """))
            rows = result.fetchall()
            print(f"   Queried {len(rows)} sample events successfully")
            
            print("\n" + "=" * 70)
            print("MIGRATION COMPLETE - Camera images can now be stored with events!")
            print("=" * 70)
            
            return True
            
        except Exception as e:
            print(f"\n❌ Migration failed: {e}")
            db.session.rollback()
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    print("\n🚀 Starting EventLog image columns migration...\n")
    
    success = migrate_add_image_columns()
    
    if success:
        print("\n✅ Migration successful!")
        sys.exit(0)
    else:
        print("\n❌ Migration failed!")
        sys.exit(1)
