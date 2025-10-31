#!/usr/bin/env python3
"""
Migration script to add validation_document table for uploaded IQ/OQ/PQ PDFs
STANDALONE - Does not import Flask app
"""

import sqlite3
import sys
import os

# Database path
DB_PATH = 'door_alarm.db'

def migrate():
    """Add validation_document table"""
    
    # Check if database exists
    if not os.path.exists(DB_PATH):
        print(f"❌ Database file '{DB_PATH}' not found!")
        sys.exit(1)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("🔧 Starting migration: Add validation_document table...")
    
    try:
        # Check if table already exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='validation_document'
        """)
        
        if cursor.fetchone():
            print("ℹ️  Table 'validation_document' already exists. Skipping migration.")
            return
        
        # Create validation_document table
        cursor.execute("""
            CREATE TABLE validation_document (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_number VARCHAR(100) UNIQUE NOT NULL,
                document_type VARCHAR(20) NOT NULL,
                original_filename VARCHAR(255) NOT NULL,
                file_path VARCHAR(500) NOT NULL,
                file_size INTEGER,
                system_id VARCHAR(100),
                software_version VARCHAR(50),
                site_location VARCHAR(200),
                uploaded_by INTEGER NOT NULL,
                uploaded_at DATETIME NOT NULL,
                status VARCHAR(20) DEFAULT 'pending',
                submitted_at DATETIME,
                approved_by INTEGER,
                approved_at DATETIME,
                rejection_reason TEXT,
                description TEXT,
                notes TEXT,
                FOREIGN KEY (uploaded_by) REFERENCES user(id),
                FOREIGN KEY (approved_by) REFERENCES user(id)
            )
        """)
        
        conn.commit()
        print("✅ Table 'validation_document' created successfully")
        
        # Verify table structure
        cursor.execute("PRAGMA table_info(validation_document)")
        columns = cursor.fetchall()
        print(f"✅ Table has {len(columns)} columns:")
        for col in columns:
            print(f"   - {col[1]} ({col[2]})")
        
    except sqlite3.Error as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
        raise
    
    finally:
        conn.close()
    
    print("🎉 Migration completed successfully!")

if __name__ == '__main__':
    migrate()
