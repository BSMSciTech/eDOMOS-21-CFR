#!/usr/bin/env python3
"""
Fix Database Schema - Force SQLAlchemy to recognize existing tables
This script will drop the company_profile and door_system_info tables and recreate them
using SQLAlchemy's create_all() method to ensure schema consistency.
"""

import os
import sys
from flask import Flask
from models import db, CompanyProfile, DoorSystemInfo
from datetime import datetime

# Create a minimal Flask app for database operations
app = Flask(__name__)
# Use absolute path to avoid directory issues
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'edomos.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

def fix_database_schema():
    """Drop and recreate company_profile and door_system_info tables"""
    with app.app_context():
        print("🔧 Fixing database schema...")
        print("=" * 60)
        
        try:
            # Check if tables exist
            print("\n1️⃣ Checking existing tables...")
            inspector = db.inspect(db.engine)
            existing_tables = inspector.get_table_names()
            print(f"   Existing tables: {existing_tables}")
            
            # Drop tables if they exist
            print("\n2️⃣ Dropping old tables...")
            if 'company_profile' in existing_tables:
                CompanyProfile.__table__.drop(db.engine)
                print("   ✅ Dropped company_profile table")
            else:
                print("   ℹ️  company_profile table doesn't exist")
                
            if 'door_system_info' in existing_tables:
                DoorSystemInfo.__table__.drop(db.engine)
                print("   ✅ Dropped door_system_info table")
            else:
                print("   ℹ️  door_system_info table doesn't exist")
            
            # Recreate tables using SQLAlchemy models
            print("\n3️⃣ Creating tables from SQLAlchemy models...")
            CompanyProfile.__table__.create(db.engine)
            print("   ✅ Created company_profile table")
            
            DoorSystemInfo.__table__.create(db.engine)
            print("   ✅ Created door_system_info table")
            
            # Verify tables were created correctly
            print("\n4️⃣ Verifying table structure...")
            inspector = db.inspect(db.engine)
            
            # Check company_profile columns
            cp_columns = [col['name'] for col in inspector.get_columns('company_profile')]
            print(f"   company_profile columns ({len(cp_columns)}): {', '.join(cp_columns)}")
            
            if 'logo_path' in cp_columns:
                print("   ✅ logo_path column exists in company_profile")
            else:
                print("   ❌ logo_path column MISSING from company_profile")
                return False
            
            # Check door_system_info columns
            dsi_columns = [col['name'] for col in inspector.get_columns('door_system_info')]
            print(f"   door_system_info columns ({len(dsi_columns)}): {', '.join(dsi_columns)}")
            
            # Insert default data
            print("\n5️⃣ Inserting default data...")
            
            # Add default company profile
            default_company = CompanyProfile(
                company_name='eDOMOS Security Systems',
                company_address='123 Main Street',
                company_city='Tech City',
                company_state='CA',
                company_country='USA',
                company_phone='+1-555-0100',
                company_email='admin@edomos.com',
                updated_at=datetime.utcnow()
            )
            db.session.add(default_company)
            print("   ✅ Added default company profile")
            
            # Add default door system info
            default_door = DoorSystemInfo(
                door_location='Main Entrance',
                department_name='Security',
                device_serial_number='EDOMOS-2024-001',
                system_model='eDOMOS v2.1',
                installation_date=datetime.utcnow().date(),
                is_active=True,
                updated_at=datetime.utcnow()
            )
            db.session.add(default_door)
            print("   ✅ Added default door system info")
            
            # Commit changes
            db.session.commit()
            print("   ✅ Changes committed to database")
            
            print("\n" + "=" * 60)
            print("✅ Database schema fix completed successfully!")
            print("\n📝 Next steps:")
            print("   1. Start the application: python3 app.py")
            print("   2. Go to Company Profile page")
            print("   3. Try uploading a logo - it should work now!")
            print("=" * 60)
            
            return True
            
        except Exception as e:
            print(f"\n❌ Error fixing database schema: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = fix_database_schema()
    sys.exit(0 if success else 1)
