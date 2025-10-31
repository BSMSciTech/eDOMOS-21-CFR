#!/usr/bin/env python3
"""
Blockchain Migration Script for eDOMOS
Creates blockchain table and optionally migrates existing events

Usage:
    python blockchain_migration.py
"""

from app import app, db
from models import BlockchainEventLog, EventLog
from blockchain_helper import create_genesis_block, add_blockchain_event
from datetime import datetime


def create_blockchain_table():
    """Create the blockchain event log table"""
    print("\n" + "="*60)
    print("eDOMOS BLOCKCHAIN MIGRATION")
    print("="*60)
    
    with app.app_context():
        # Create the table
        db.create_all()
        print("✅ BlockchainEventLog table created successfully!")
        
        # Check if blockchain already exists
        existing_blocks = BlockchainEventLog.query.count()
        if existing_blocks > 0:
            print(f"ℹ️  Blockchain already exists with {existing_blocks} blocks")
            return
        
        # Create genesis block
        print("\n📦 Creating genesis block...")
        genesis = create_genesis_block()
        print(f"✅ Genesis block created!")
        print(f"   Block Index: {genesis.block_index}")
        print(f"   Hash: {genesis.block_hash}")
        print(f"   Timestamp: {genesis.timestamp}")
        
        # Ask about migrating existing events
        print("\n" + "-"*60)
        existing_events = EventLog.query.count()
        if existing_events > 0:
            print(f"📊 Found {existing_events} existing events in EventLog table")
            response = input(f"\nMigrate these {existing_events} events to blockchain? (yes/no): ")
            
            if response.lower() in ['yes', 'y']:
                migrate_existing_events()
            else:
                print("⏭️  Skipping migration of existing events")
        else:
            print("ℹ️  No existing events to migrate")
        
        print("\n" + "="*60)
        print("✅ BLOCKCHAIN MIGRATION COMPLETE!")
        print("="*60)
        print("\nYour event logs are now blockchain-verified!")
        print("All future events will be cryptographically secured.\n")


def migrate_existing_events():
    """Migrate existing events from EventLog to BlockchainEventLog"""
    with app.app_context():
        events = EventLog.query.order_by(EventLog.timestamp).all()
        total = len(events)
        
        print(f"\n🔄 Migrating {total} events to blockchain...")
        print("This may take a moment...\n")
        
        migrated = 0
        for i, event in enumerate(events, 1):
            try:
                # Add to blockchain
                add_blockchain_event(
                    event_type=event.event_type,
                    description=f"[MIGRATED] {event.description}",
                    user_id=None,
                    ip_address=None
                )
                migrated += 1
                
                # Progress indicator
                if i % 10 == 0 or i == total:
                    print(f"   Progress: {i}/{total} events migrated ({int(i/total*100)}%)")
                
            except Exception as e:
                print(f"   ⚠️  Error migrating event {event.id}: {str(e)}")
        
        print(f"\n✅ Successfully migrated {migrated}/{total} events to blockchain")
        
        # Verify the blockchain
        from blockchain_helper import verify_blockchain
        is_valid, message, corrupted = verify_blockchain()
        
        if is_valid:
            print(f"✅ Blockchain verification: {message}")
        else:
            print(f"⚠️  Blockchain verification failed: {message}")


def show_blockchain_stats():
    """Display blockchain statistics"""
    with app.app_context():
        from blockchain_helper import get_blockchain_stats
        
        stats = get_blockchain_stats()
        
        print("\n" + "="*60)
        print("BLOCKCHAIN STATISTICS")
        print("="*60)
        
        if not stats['blockchain_exists']:
            print("❌ No blockchain found")
            return
        
        print(f"Total Blocks: {stats['total_blocks']}")
        print(f"Blockchain Verified: {'✅ YES' if stats['verified'] else '❌ NO'}")
        print(f"Verification: {stats['verification_message']}")
        print(f"Genesis Block: {stats['genesis_timestamp']}")
        print(f"Latest Block: {stats['latest_timestamp']}")
        print(f"Latest Index: {stats['latest_block_index']}")
        
        print("\nEvent Breakdown:")
        for event_type, count in stats['event_breakdown'].items():
            print(f"  {event_type}: {count}")
        
        print("="*60 + "\n")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'stats':
        show_blockchain_stats()
    else:
        create_blockchain_table()
