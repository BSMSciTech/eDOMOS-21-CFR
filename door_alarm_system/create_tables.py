#!/usr/bin/env python3
"""
Script to create company_profile and door_system_info tables
"""
import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).parent / 'instance' / 'edomos.db'

def create_tables():
    """Create company_profile and door_system_info tables"""
    
    print("🔧 Connecting to database...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Drop existing tables if they exist
        print("\n🗑️  Dropping existing tables...")
        cursor.execute("DROP TABLE IF EXISTS company_profile")
        cursor.execute("DROP TABLE IF EXISTS door_system_info")
        conn.commit()
        print("✅ Existing tables dropped")
        
        # Create company_profile table
        print("\n📋 Creating company_profile table...")
        cursor.execute("""
            CREATE TABLE company_profile (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name VARCHAR(200) NOT NULL,
                company_address TEXT,
                company_city VARCHAR(100),
                company_state VARCHAR(100),
                company_zip VARCHAR(20),
                company_country VARCHAR(100),
                company_phone VARCHAR(20),
                company_email VARCHAR(120),
                company_website VARCHAR(200),
                logo_path VARCHAR(500),
                updated_at DATETIME
            )
        """)
        conn.commit()
        print("✅ company_profile table created")
        
        # Create door_system_info table
        print("\n📋 Creating door_system_info table...")
        cursor.execute("""
            CREATE TABLE door_system_info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                door_location VARCHAR(200) NOT NULL,
                department_name VARCHAR(100),
                device_serial_number VARCHAR(100),
                system_model VARCHAR(100),
                installation_date DATE,
                last_maintenance_date DATE,
                notes TEXT,
                is_active BOOLEAN,
                updated_at DATETIME
            )
        """)
        conn.commit()
        print("✅ door_system_info table created")
        
        # Insert default data for company_profile
        print("\n📝 Inserting default company profile...")
        cursor.execute("""
            INSERT INTO company_profile 
            (company_name, company_address, company_city, company_state, 
             company_country, company_phone, company_email, updated_at)
            VALUES 
            ('eDOMOS Security Systems', '123 Main Street', 'Tech City', 'CA',
             'USA', '+1-555-0100', 'admin@edomos.com', datetime('now'))
        """)
        conn.commit()
        print("✅ Default company profile created")
        
        # Insert default data for door_system_info
        print("\n📝 Inserting default door system info...")
        cursor.execute("""
            INSERT INTO door_system_info 
            (door_location, department_name, device_serial_number, 
             system_model, is_active, updated_at)
            VALUES 
            ('Main Entrance', 'Security', 'EDOMOS-001', 
             'eDOMOS v2.1', 1, datetime('now'))
        """)
        conn.commit()
        print("✅ Default door system info created")
        
        # Verify tables
        print("\n🔍 Verifying tables...")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()
        print(f"✅ Database tables: {[t[0] for t in tables]}")
        
        # Check company_profile columns
        cursor.execute("PRAGMA table_info(company_profile)")
        cols = cursor.fetchall()
        print(f"\n✅ company_profile columns ({len(cols)}):")
        for col in cols:
            print(f"   - {col[1]} ({col[2]})")
        
        # Check door_system_info columns
        cursor.execute("PRAGMA table_info(door_system_info)")
        cols = cursor.fetchall()
        print(f"\n✅ door_system_info columns ({len(cols)}):")
        for col in cols:
            print(f"   - {col[1]} ({col[2]})")
        
        # Check data
        cursor.execute("SELECT COUNT(*) FROM company_profile")
        cp_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM door_system_info")
        ds_count = cursor.fetchone()[0]
        
        print(f"\n✅ Data verification:")
        print(f"   - CompanyProfile records: {cp_count}")
        print(f"   - DoorSystemInfo records: {ds_count}")
        
        print("\n✅ ✅ ✅ Tables created successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == '__main__':
    success = create_tables()
    sys.exit(0 if success else 1)
