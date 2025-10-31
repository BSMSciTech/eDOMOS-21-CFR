#!/usr/bin/env python3
"""
Database Migration Script for eDOMOS v2.1
Adds new tables and columns for company profile, door/system info, and extended user profiles
"""

import sys
from app import app, db
from models import User, CompanyProfile, DoorSystemInfo, Setting, EventLog, EmailConfig
from sqlalchemy import inspect, text

def check_column_exists(table_name, column_name):
    """Check if a column exists in a table"""
    inspector = inspect(db.engine)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns

def check_table_exists(table_name):
    """Check if a table exists"""
    inspector = inspect(db.engine)
    return table_name in inspector.get_table_names()

def migrate_database():
    """Perform database migration"""
    print("=" * 60)
    print("eDOMOS v2.1 - Database Migration Tool")
    print("=" * 60)
    print()
    
    with app.app_context():
        print("📊 Checking current database structure...")
        print()
        
        # Check existing tables
        inspector = inspect(db.engine)
        existing_tables = inspector.get_table_names()
        print(f"✓ Found {len(existing_tables)} existing tables: {', '.join(existing_tables)}")
        print()
        
        # Migrate User table (add new columns)
        print("👤 Migrating User table...")
        user_columns_to_add = [
            ('full_name', 'VARCHAR(150)'),
            ('employee_id', 'VARCHAR(50)'),  # Remove UNIQUE constraint for SQLite compatibility
            ('department', 'VARCHAR(100)'),
            ('role', 'VARCHAR(100)'),
            ('email', 'VARCHAR(120)'),
            ('phone', 'VARCHAR(20)'),
            ('created_at', 'TIMESTAMP'),  # Remove DEFAULT for SQLite compatibility
            ('last_login', 'TIMESTAMP'),
            ('is_active', 'BOOLEAN DEFAULT 1')
        ]
        
        added_columns = 0
        for col_name, col_type in user_columns_to_add:
            if not check_column_exists('user', col_name):
                try:
                    db.session.execute(text(f'ALTER TABLE user ADD COLUMN {col_name} {col_type}'))
                    db.session.commit()
                    print(f"  ✓ Added column: user.{col_name}")
                    added_columns += 1
                except Exception as e:
                    print(f"  ⚠ Could not add user.{col_name}: {e}")
                    db.session.rollback()
            else:
                print(f"  ℹ Column already exists: user.{col_name}")
        
        if added_columns > 0:
            print(f"  ✓ Added {added_columns} new columns to User table")
        else:
            print("  ✓ User table is up to date")
        print()
        
        # Create CompanyProfile table
        print("🏢 Creating CompanyProfile table...")
        if not check_table_exists('company_profile'):
            try:
                CompanyProfile.__table__.create(db.engine)
                print("  ✓ CompanyProfile table created successfully")
                
                # Initialize with default company profile
                default_company = CompanyProfile(
                    company_name="Your Company Name",
                    company_address="123 Main Street",
                    company_city="City",
                    company_state="State",
                    company_zip="00000",
                    company_country="Country",
                    company_phone="+1-234-567-8900",
                    company_email="info@yourcompany.com",
                    company_website="www.yourcompany.com"
                )
                db.session.add(default_company)
                db.session.commit()
                print("  ✓ Default company profile initialized")
            except Exception as e:
                print(f"  ⚠ Error creating CompanyProfile table: {e}")
                db.session.rollback()
        else:
            print("  ℹ CompanyProfile table already exists")
        print()
        
        # Create DoorSystemInfo table
        print("🚪 Creating DoorSystemInfo table...")
        if not check_table_exists('door_system_info'):
            try:
                DoorSystemInfo.__table__.create(db.engine)
                print("  ✓ DoorSystemInfo table created successfully")
                
                # Initialize with default door/system info
                default_system = DoorSystemInfo(
                    door_location="Main Entrance",
                    department_name="Security",
                    device_serial_number="EDOMOS-001",
                    system_model="eDOMOS v2.1"
                )
                db.session.add(default_system)
                db.session.commit()
                print("  ✓ Default door/system info initialized")
            except Exception as e:
                print(f"  ⚠ Error creating DoorSystemInfo table: {e}")
                db.session.rollback()
        else:
            print("  ℹ DoorSystemInfo table already exists")
        print()
        
        # Update existing users with default values
        print("🔄 Updating existing users with default profile values...")
        try:
            users = User.query.filter(User.full_name == None).all()
            updated_count = 0
            for user in users:
                user.full_name = user.username.title()
                user.employee_id = f"EMP{user.id:04d}"
                user.department = "General"
                user.role = "Administrator" if user.is_admin else "User"
                user.is_active = True
                updated_count += 1
            
            if updated_count > 0:
                db.session.commit()
                print(f"  ✓ Updated {updated_count} existing users with default profile values")
            else:
                print("  ℹ All users already have profile data")
        except Exception as e:
            print(f"  ⚠ Error updating users: {e}")
            db.session.rollback()
        print()
        
        # Final verification
        print("✅ MIGRATION SUMMARY:")
        print("=" * 60)
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        for table in ['user', 'company_profile', 'door_system_info', 'setting', 'event_log', 'email_config']:
            if table in tables:
                columns = inspector.get_columns(table)
                print(f"  ✓ {table}: {len(columns)} columns")
            else:
                print(f"  ✗ {table}: NOT FOUND")
        
        print()
        print("🎉 Database migration completed successfully!")
        print()
        print("📝 Next steps:")
        print("  1. Restart the application: python app.py")
        print("  2. Login as admin")
        print("  3. Navigate to Settings to configure company profile")
        print("  4. Navigate to Settings to configure door/system information")
        print("  5. Update user profiles from the Admin panel")
        print()

if __name__ == '__main__':
    try:
        migrate_database()
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
