"""
Migration script to add ai_metadata column to event_log table
"""

from app import app, db
from sqlalchemy import text

with app.app_context():
    try:
        # Check if column already exists
        result = db.session.execute(text("PRAGMA table_info(event_log)"))
        columns = [row[1] for row in result]
        
        if 'ai_metadata' not in columns:
            print("Adding ai_metadata column to event_log table...")
            db.session.execute(text('ALTER TABLE event_log ADD COLUMN ai_metadata TEXT'))
            db.session.commit()
            print("✅ Migration successful: ai_metadata column added")
        else:
            print("ℹ️  ai_metadata column already exists, skipping migration")
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        db.session.rollback()
        raise
