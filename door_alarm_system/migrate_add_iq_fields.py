#!/usr/bin/env python3
"""
Migration script to add IQ-specific fields to ValidationTest table
Adds fields for complete FDA 21 CFR Part 11 compliant Installation Qualification
"""

import sqlite3
import os

def migrate_iq_fields():
    """Add IQ-specific columns to validation_test table"""
    db_path = 'instance/alarm_system.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Database {db_path} not found!")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='validation_test'")
        if not cursor.fetchone():
            print("❌ Table 'validation_test' does not exist.")
            return False
        
        # Get existing columns
        cursor.execute("PRAGMA table_info(validation_test)")
        existing_columns = [col[1] for row in cursor.fetchall()]
        print(f"✅ Found {len(existing_columns)} existing columns")
        
        # Define new IQ-specific columns to add
        new_columns = {
            'manufacturer_info': "ALTER TABLE validation_test ADD COLUMN manufacturer_info TEXT",
            'customer_info': "ALTER TABLE validation_test ADD COLUMN customer_info TEXT",
            'scope_statement': "ALTER TABLE validation_test ADD COLUMN scope_statement TEXT",
            'purpose_statement': "ALTER TABLE validation_test ADD COLUMN purpose_statement TEXT",
            'responsibilities': "ALTER TABLE validation_test ADD COLUMN responsibilities TEXT",
            'pre_installation_checklist': "ALTER TABLE validation_test ADD COLUMN pre_installation_checklist TEXT",
            'hardware_verification': "ALTER TABLE validation_test ADD COLUMN hardware_verification TEXT",
            'software_verification': "ALTER TABLE validation_test ADD COLUMN software_verification TEXT",
            'documentation_verification': "ALTER TABLE validation_test ADD COLUMN documentation_verification TEXT",
            'deviation_log': "ALTER TABLE validation_test ADD COLUMN deviation_log TEXT",
            'conclusion_statement': "ALTER TABLE validation_test ADD COLUMN conclusion_statement TEXT",
            'document_version': "ALTER TABLE validation_test ADD COLUMN document_version VARCHAR(20) DEFAULT '1.0'",
            'is_locked': "ALTER TABLE validation_test ADD COLUMN is_locked BOOLEAN DEFAULT 0",
            'approved_by': "ALTER TABLE validation_test ADD COLUMN approved_by INTEGER",
            'approved_date': "ALTER TABLE validation_test ADD COLUMN approved_date DATETIME",
            'approval_signature_id': "ALTER TABLE validation_test ADD COLUMN approval_signature_id INTEGER",
            'prepared_date': "ALTER TABLE validation_test ADD COLUMN prepared_date DATETIME"
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
        print(f"   Added {added_count} new IQ-specific columns")
        
        # Show updated table structure
        cursor.execute("PRAGMA table_info(validation_test)")
        columns = cursor.fetchall()
        print(f"\n📋 Updated table structure ({len(columns)} total columns):")
        
        # Group by category
        iq_fields = ['manufacturer_info', 'customer_info', 'scope_statement', 'purpose_statement', 
                     'responsibilities', 'pre_installation_checklist', 'hardware_verification',
                     'software_verification', 'documentation_verification', 'deviation_log',
                     'conclusion_statement', 'document_version', 'is_locked', 'approved_by',
                     'approved_date', 'approval_signature_id', 'prepared_date']
        
        print("\n🏭 IQ-Specific Fields:")
        for col in columns:
            if col[1] in iq_fields:
                print(f"   ✅ {col[1]} ({col[2]})")
        
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()

if __name__ == '__main__':
    print("="*70)
    print("IQ (Installation Qualification) Fields Migration")
    print("Adding FDA 21 CFR Part 11 compliant fields to ValidationTest")
    print("="*70)
    print()
    
    success = migrate_iq_fields()
    
    if success:
        print("\n✅ Migration successful!")
        print("📝 You can now create comprehensive IQ documents with:")
        print("   - Document header (manufacturer, customer info)")
        print("   - Purpose & scope statements")
        print("   - Responsibilities matrix")
        print("   - Pre-installation checklist")
        print("   - Hardware/software verification")
        print("   - Documentation verification")
        print("   - Deviation/non-conformance log")
        print("   - Digital signatures (prepared, verified, approved)")
        print("   - Version control and document locking")
    else:
        print("\n❌ Migration failed. Please check the errors above.")
