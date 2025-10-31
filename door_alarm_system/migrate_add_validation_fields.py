#!/usr/bin/env python3
"""
Migration script to add new fields to ValidationTest table
- Equipment information (name, model, serial)
- Test category
- Prerequisites
- Acceptance criteria
"""

import sqlite3
import os

def migrate_validation_test_table():
    """Add new columns to validation_test table"""
    db_path = 'door_alarm.db'
    
    if not os.path.exists(db_path):
        print(f"Database {db_path} not found!")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='validation_test'")
        if not cursor.fetchone():
            print("Table 'validation_test' does not exist. No migration needed.")
            return True
        
        # Get existing columns
        cursor.execute("PRAGMA table_info(validation_test)")
        existing_columns = [col[1] for col in cursor.fetchall()]
        print(f"Existing columns: {existing_columns}")
        
        # Define new columns to add
        new_columns = {
            'equipment_name': "ALTER TABLE validation_test ADD COLUMN equipment_name VARCHAR(200)",
            'equipment_model': "ALTER TABLE validation_test ADD COLUMN equipment_model VARCHAR(100)",
            'equipment_serial': "ALTER TABLE validation_test ADD COLUMN equipment_serial VARCHAR(100)",
            'test_category': "ALTER TABLE validation_test ADD COLUMN test_category VARCHAR(50)",
            'prerequisites': "ALTER TABLE validation_test ADD COLUMN prerequisites TEXT",
            'acceptance_criteria': "ALTER TABLE validation_test ADD COLUMN acceptance_criteria TEXT"
        }
        
        # Add each column if it doesn't exist
        added_count = 0
        for col_name, alter_sql in new_columns.items():
            if col_name not in existing_columns:
                print(f"Adding column: {col_name}")
                cursor.execute(alter_sql)
                added_count += 1
            else:
                print(f"Column {col_name} already exists, skipping")
        
        conn.commit()
        print(f"\n✅ Migration completed successfully!")
        print(f"   Added {added_count} new columns to validation_test table")
        
        # Show updated table structure
        cursor.execute("PRAGMA table_info(validation_test)")
        columns = cursor.fetchall()
        print(f"\n📋 Updated table structure ({len(columns)} columns):")
        for col in columns:
            print(f"   - {col[1]} ({col[2]})")
        
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()

if __name__ == '__main__':
    print("="*60)
    print("ValidationTest Table Migration")
    print("Adding: Equipment Info, Category, Prerequisites, Acceptance Criteria")
    print("="*60)
    print()
    
    success = migrate_validation_test_table()
    
    if success:
        print("\n✅ Migration successful! You can now use the new validation fields.")
    else:
        print("\n❌ Migration failed. Please check the errors above.")
