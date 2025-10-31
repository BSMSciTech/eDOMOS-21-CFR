#!/usr/bin/env python3
"""
Quick migration script for 21 CFR Part 11 tables
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import (
    ElectronicSignature, 
    TrainingModule, 
    TrainingRecord, 
    ChangeControl,
    StandardOperatingProcedure,
    ValidationTest,
    User
)
from datetime import datetime

def main():
    with app.app_context():
        try:
            print("Creating 21 CFR Part 11 compliance tables...")
            db.create_all()
            print("✓ Tables created successfully\n")
            
            # Verify tables
            inspector = db.inspect(db.engine)
            existing_tables = inspector.get_table_names()
            
            required_tables = [
                'electronic_signature',
                'training_module', 
                'training_record',
                'change_control',
                'sop',
                'validation_test'
            ]
            
            print("Table verification:")
            for table in required_tables:
                status = "✓" if table in existing_tables else "✗"
                print(f"  {status} {table}")
            
            print("\nMigration complete!")
            return True
            
        except Exception as e:
            print(f"\n✗ Migration failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
