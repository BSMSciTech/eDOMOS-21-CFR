#!/usr/bin/env python3
"""
Migration script to add 21 CFR Part 11 compliance tables
Creates: electronic_signature, training_module, training_record, change_control, sop, validation_test
"""

import sys
import os
from datetime import datetime

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

def migrate_add_part11_tables():
    """Add 21 CFR Part 11 compliance tables to database"""
    
    with app.app_context():
        try:
            # Create all new tables
            print("Creating 21 CFR Part 11 compliance tables...")
            db.create_all()
            print("✓ Tables created successfully")
            
            # Verify tables were created
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
            
            print("\nVerifying table creation:")
            all_created = True
            for table in required_tables:
                if table in existing_tables:
                    print(f"✓ {table}")
                else:
                    print(f"✗ {table} - MISSING")
                    all_created = False
            
            if all_created:
                print("\n✓ All 21 CFR Part 11 tables created successfully!")
                print("\nCreated tables:")
                print("  - electronic_signature: Electronic signature records (§11.50, §11.100, §11.200)")
                print("  - training_module: Training content and requirements (§11.10(i))")
                print("  - training_record: Training completion tracking (§11.10(i))")
                print("  - change_control: Change request and approval workflow (§11.10(k)(2))")
                print("  - sop: Standard Operating Procedures (§11.10)")
                print("  - validation_test: IQ/OQ/PQ validation records (§11.10(a))")
                
                # Create initial SOP for system validation
                create_initial_sop()
                
                # Create initial training module
                create_initial_training()
                
                return True
            else:
                print("\n✗ Some tables failed to create. Check database connection and model definitions.")
                return False
                
        except Exception as e:
            print(f"\n✗ Migration failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

def create_initial_sop():
    """Create initial SOP for 21 CFR Part 11 compliance"""
    try:
        # Get admin user (assuming user ID 1 is admin)
        admin = db.session.query(User).filter_by(id=1).first()
        if not admin:
            print("\n⚠ Warning: No admin user found (id=1). Skipping initial SOP creation.")
            return
        
        # Check if SOP already exists
        existing_sop = db.session.query(StandardOperatingProcedure).filter_by(sop_number='SOP-001').first()
        if existing_sop:
            print("\n⚠ Initial SOP already exists. Skipping creation.")
            return
        
        sop = StandardOperatingProcedure(
            sop_number='SOP-001',
            title='21 CFR Part 11 Compliance Standard Operating Procedure',
            category='Compliance',
            content="""
# Purpose
This SOP establishes procedures for maintaining compliance with 21 CFR Part 11 for electronic records and electronic signatures.

# Scope
Applies to all users of the eDOMOS Door Alarm System who create, modify, or review electronic records.

# Responsibilities
- System Administrators: Maintain system validation, manage user access
- All Users: Complete required training, use electronic signatures appropriately
- Quality Assurance: Conduct periodic audits of electronic records

# Procedures

## 1. Electronic Signatures (§11.50, §11.100, §11.200)
- Users must re-enter password to create electronic signature
- Each signature must include reason for signing
- System captures: User ID, timestamp, IP address, signature hash
- Signatures are cryptographically linked to signed records

## 2. Training Requirements (§11.10(i))
- All users must complete "21 CFR Part 11 Basics" training before system access
- Training must be renewed annually
- System tracks completion and expiration dates
- Users attest to training completion with electronic signature

## 3. Change Control (§11.10(k)(2))
- All system changes require change control record
- Changes must be reviewed and approved before implementation
- System maintains version history with before/after snapshots
- All approvals captured via electronic signature

## 4. Audit Trails (§11.10(e))
- System maintains blockchain-based audit trail
- All events immutably recorded with timestamp, user, action
- Audit trail cannot be modified or deleted
- Blockchain verified regularly for integrity

## 5. System Validation (§11.10(a))
- Initial validation completed via IQ/OQ/PQ protocol
- Revalidation required after major system changes
- Validation records maintained electronically
- Validation reviewed and approved via electronic signature

# References
- 21 CFR Part 11 - Electronic Records; Electronic Signatures
- FDA Guidance for Industry - Part 11, Electronic Records; Electronic Signatures
            """,
            version='1.0',
            status='approved',
            created_by=admin.id,
            approved_by=admin.id,
            effective_date=datetime.utcnow(),
            review_frequency_days=365
        )
        
        db.session.add(sop)
        db.session.commit()
        print(f"\n✓ Created initial SOP: {sop.sop_number} - {sop.title}")
        
    except Exception as e:
        print(f"\n⚠ Warning: Could not create initial SOP: {str(e)}")
        db.session.rollback()

def create_initial_training():
    """Create initial training module for 21 CFR Part 11"""
    try:
        # Get admin user
        admin = db.session.query(User).filter_by(id=1).first()
        if not admin:
            print("\n⚠ Warning: No admin user found (id=1). Skipping initial training creation.")
            return
        
        # Check if training module already exists
        existing_training = db.session.query(TrainingModule).filter_by(module_name='21 CFR Part 11 Basics').first()
        if existing_training:
            print("\n⚠ Initial training module already exists. Skipping creation.")
            return
        
        training = TrainingModule(
            module_name='21 CFR Part 11 Basics',
            description='Introduction to FDA regulations for electronic records and signatures',
            content="""
# 21 CFR Part 11 Training Module

## Learning Objectives
By the end of this training, you will understand:
1. What is 21 CFR Part 11 and why it matters
2. How to use electronic signatures properly
3. Your responsibilities for maintaining compliant records
4. How the system maintains audit trails

## Module 1: Introduction to 21 CFR Part 11

### What is 21 CFR Part 11?
21 CFR Part 11 is an FDA regulation that establishes requirements for electronic records and electronic signatures. It ensures that electronic records are:
- **Trustworthy** - as reliable as paper records
- **Reliable** - consistently accurate
- **Secure** - protected from unauthorized access

### Why Does It Matter?
In regulated industries (pharmaceuticals, medical devices, food & beverage), maintaining proper documentation is critical for:
- Patient safety
- Product quality
- Regulatory compliance
- Legal defensibility

## Module 2: Electronic Signatures

### What is an Electronic Signature?
An electronic signature is a computer-generated authentication that:
- Links to you uniquely
- Is created when you take an action
- Cannot be repudiated (you can't deny you did it)

### How to Use Electronic Signatures in This System
1. When you perform certain actions (approve changes, complete training, etc.)
2. System will prompt you to sign electronically
3. You must re-enter your password (this proves it's really you)
4. You must provide a reason for signing
5. System records: your user ID, timestamp, IP address, and cryptographic hash

### Rules for Electronic Signatures
- ✓ DO sign only actions you personally performed or reviewed
- ✓ DO provide meaningful reasons for signing
- ✓ DO keep your password secure and confidential
- ✗ DON'T share your login credentials with anyone
- ✗ DON'T sign for someone else
- ✗ DON'T leave your workstation unlocked

## Module 3: Your Responsibilities

### Creating Records
- Ensure accuracy of all data entered
- Use appropriate access controls
- Follow Standard Operating Procedures (SOPs)

### Maintaining Records
- Do not delete or modify records inappropriately
- Report any system issues immediately
- Participate in periodic audits

### Training
- Complete all required training on time
- Keep training records current
- Request retraining if procedures are unclear

## Module 4: System Capabilities

### Audit Trails (§11.10(e))
The system automatically creates audit trails that record:
- Who performed an action
- What action was performed
- When it was performed
- Why it was performed (for some actions)

These audit trails use **blockchain technology** which makes them:
- Immutable (cannot be changed)
- Verifiable (can prove integrity)
- Permanent (cannot be deleted)

### Access Controls (§11.10(d))
The system enforces:
- Unique user accounts
- Password complexity requirements
- Session timeouts
- Role-based permissions

### Change Control (§11.10(k))
All system changes are tracked through formal change control:
- Change requests documented
- Risk assessment performed
- Approvals required before implementation
- Version history maintained

## Assessment
To complete this training, you must:
1. Review all content above
2. Score 80% or higher on the quiz (to be implemented)
3. Sign attestation electronically

## Quiz (Placeholder)
1. What does 21 CFR Part 11 regulate?
2. When must you use an electronic signature?
3. Can you share your password with a colleague?
4. What is the purpose of an audit trail?
5. Who is responsible for the accuracy of records you create?

## Attestation
By signing below, I attest that:
- I have reviewed and understand this training material
- I will follow all 21 CFR Part 11 requirements
- I will maintain the confidentiality of my login credentials
- I understand my responsibilities for creating accurate records
            """,
            required_for_roles='all',
            validity_period_days=365,
            version='1.0',
            created_by=admin.id
        )
        
        db.session.add(training)
        db.session.commit()
        print(f"\n✓ Created initial training module: {training.module_name}")
        print(f"  - Validity: {training.validity_period_days} days")
        print(f"  - Required for: {training.required_for_roles}")
        
    except Exception as e:
        print(f"\n⚠ Warning: Could not create initial training: {str(e)}")
        db.session.rollback()

if __name__ == '__main__':
    print("=" * 70)
    print("21 CFR Part 11 Compliance Migration")
    print("=" * 70)
    print("\nThis migration will create the following tables:")
    print("  1. electronic_signature - Electronic signature records")
    print("  2. training_module - Training content")
    print("  3. training_record - Training completion tracking")
    print("  4. change_control - Change management")
    print("  5. sop - Standard Operating Procedures")
    print("  6. validation_test - IQ/OQ/PQ validation")
    print("\n" + "=" * 70)
    
    response = input("\nProceed with migration? (yes/no): ")
    
    if response.lower() in ['yes', 'y']:
        success = migrate_add_part11_tables()
        if success:
            print("\n" + "=" * 70)
            print("MIGRATION SUCCESSFUL!")
            print("=" * 70)
            print("\nNext steps:")
            print("  1. Implement electronic signature capture UI")
            print("  2. Build training management system")
            print("  3. Create change control workflow")
            print("  4. Develop validation test suite")
            print("\nYour system is now ready for 21 CFR Part 11 compliance features!")
            sys.exit(0)
        else:
            print("\n" + "=" * 70)
            print("MIGRATION FAILED")
            print("=" * 70)
            sys.exit(1)
    else:
        print("\nMigration cancelled.")
        sys.exit(0)
