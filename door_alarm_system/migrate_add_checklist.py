#!/usr/bin/env python3
"""
Migration script to add change_control_checklist_item table
Run this to enable customizable review checklists
"""

from app import app, db
from models import ChangeControlChecklistItem

def migrate():
    """Add checklist items table and populate with default items"""
    with app.app_context():
        print("Creating change_control_checklist_item table...")
        
        # Create table
        db.create_all()
        
        # Check if default items already exist
        existing_count = ChangeControlChecklistItem.query.count()
        if existing_count > 0:
            print(f"✓ Table already exists with {existing_count} items")
            return
        
        print("Adding default checklist items...")
        
        # Default checklist items (generic, suitable for most companies)
        default_items = [
            {
                'item_text': 'Change description is clear and complete',
                'description': 'Verify that the change description provides sufficient detail to understand what will be modified',
                'display_order': 1,
                'is_active': True
            },
            {
                'item_text': 'Business justification is valid',
                'description': 'Confirm there is a legitimate business or technical reason for this change',
                'display_order': 2,
                'is_active': True
            },
            {
                'item_text': 'Risk assessment is adequate',
                'description': 'Ensure potential risks and impacts have been properly analyzed and documented',
                'display_order': 3,
                'is_active': True
            },
            {
                'item_text': 'Rollback plan is acceptable',
                'description': 'Verify there is a clear procedure to revert the change if issues occur',
                'display_order': 4,
                'is_active': True
            },
            {
                'item_text': 'Priority level is appropriate',
                'description': 'Confirm the assigned priority (low/medium/high/critical) matches the urgency and impact',
                'display_order': 5,
                'is_active': True
            },
            {
                'item_text': 'Affected systems are identified',
                'description': 'All impacted systems, modules, or components are listed',
                'display_order': 6,
                'is_active': True
            },
            {
                'item_text': 'Testing requirements defined',
                'description': 'Appropriate testing plan exists to validate the change',
                'display_order': 7,
                'is_active': True
            },
            {
                'item_text': 'Documentation will be updated',
                'description': 'User manuals, SOPs, or training materials will be revised as needed',
                'display_order': 8,
                'is_active': True
            }
        ]
        
        # Add items to database
        for item_data in default_items:
            item = ChangeControlChecklistItem(**item_data)
            db.session.add(item)
        
        db.session.commit()
        print(f"✓ Added {len(default_items)} default checklist items")
        print("\n" + "="*60)
        print("✓ Migration completed successfully!")
        print("="*60)
        print("\nDefault checklist items:")
        for idx, item in enumerate(default_items, 1):
            print(f"  {idx}. {item['item_text']}")
        print("\n✓ Admins can now customize these items in the admin panel")

if __name__ == '__main__':
    migrate()
