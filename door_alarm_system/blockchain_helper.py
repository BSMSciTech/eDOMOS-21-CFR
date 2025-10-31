"""
Blockchain Audit Trail Helper Functions
Provides tamper-proof event logging with cryptographic verification
"""

import hashlib
import json
from datetime import datetime
from models import BlockchainEventLog, db
from flask import request
from flask_login import current_user


def create_genesis_block():
    """Create the first block in the blockchain"""
    genesis = BlockchainEventLog(
        block_index=0,
        event_type='genesis',
        description='Blockchain initialized - eDOMOS v2.1',
        timestamp=datetime.utcnow(),
        previous_hash='0' * 64,
        nonce=0
    )
    genesis.block_hash = genesis.calculate_hash()
    
    db.session.add(genesis)
    db.session.commit()
    
    return genesis


def get_latest_block():
    """Get the most recent block in the chain"""
    return BlockchainEventLog.query.order_by(BlockchainEventLog.block_index.desc()).first()


def add_blockchain_event(event_type, description, user_id=None, ip_address=None):
    """
    Add a new event to the blockchain
    
    Args:
        event_type: Type of event (door_open, door_close, alarm_triggered, etc.)
        description: Event description
        user_id: Optional user ID who triggered the event
        ip_address: Optional IP address
    
    Returns:
        BlockchainEventLog: The created block
    """
    # Get the previous block
    previous_block = get_latest_block()
    
    if previous_block is None:
        # No blockchain exists, create genesis block
        previous_block = create_genesis_block()
    
    # Get user info if available
    if user_id is None and hasattr(current_user, 'id') and current_user.is_authenticated:
        user_id = current_user.id
    
    if ip_address is None and request:
        ip_address = request.remote_addr
    
    # Create new block
    new_block = BlockchainEventLog(
        block_index=previous_block.block_index + 1,
        event_type=event_type,
        description=description,
        timestamp=datetime.utcnow(),
        previous_hash=previous_block.block_hash,
        nonce=0,
        user_id=user_id,
        ip_address=ip_address
    )
    
    # Calculate hash
    new_block.block_hash = new_block.calculate_hash()
    
    # Save to database
    db.session.add(new_block)
    db.session.commit()
    
    return new_block


def verify_blockchain():
    """
    Verify the entire blockchain for tampering
    
    Returns:
        tuple: (is_valid: bool, message: str, corrupted_blocks: list)
    """
    blocks = BlockchainEventLog.query.order_by(BlockchainEventLog.block_index).all()
    
    if len(blocks) == 0:
        return False, "No blockchain found", []
    
    corrupted_blocks = []
    
    for i, block in enumerate(blocks):
        # Check 1: Verify block's hash is correct
        calculated_hash = block.calculate_hash()
        if block.block_hash != calculated_hash:
            corrupted_blocks.append({
                'block_index': block.block_index,
                'reason': 'Block hash mismatch',
                'stored_hash': block.block_hash,
                'calculated_hash': calculated_hash
            })
        
        # Check 2: Verify link to previous block (skip genesis)
        if i > 0:
            previous_block = blocks[i - 1]
            if block.previous_hash != previous_block.block_hash:
                corrupted_blocks.append({
                    'block_index': block.block_index,
                    'reason': 'Chain broken - previous hash mismatch',
                    'expected': previous_block.block_hash,
                    'actual': block.previous_hash
                })
    
    if corrupted_blocks:
        return False, f"Blockchain corrupted! {len(corrupted_blocks)} block(s) compromised", corrupted_blocks
    
    return True, f"Blockchain verified: {len(blocks)} blocks intact", []


def get_blockchain_stats():
    """Get statistics about the blockchain"""
    total_blocks = BlockchainEventLog.query.count()
    
    if total_blocks == 0:
        return {
            'total_blocks': 0,
            'blockchain_exists': False,
            'verified': False
        }
    
    latest_block = get_latest_block()
    genesis_block = BlockchainEventLog.query.filter_by(block_index=0).first()
    
    is_valid, message, corrupted = verify_blockchain()
    
    # Count events by type
    from sqlalchemy import func
    event_counts = db.session.query(
        BlockchainEventLog.event_type,
        func.count(BlockchainEventLog.id)
    ).group_by(BlockchainEventLog.event_type).all()
    
    event_breakdown = {event_type: count for event_type, count in event_counts}
    
    return {
        'total_blocks': total_blocks,
        'blockchain_exists': True,
        'verified': is_valid,
        'verification_message': message,
        'corrupted_blocks': len(corrupted),
        'genesis_timestamp': genesis_block.timestamp.strftime('%Y-%m-%d %H:%M:%S') if genesis_block else None,
        'latest_timestamp': latest_block.timestamp.strftime('%Y-%m-%d %H:%M:%S') if latest_block else None,
        'latest_block_index': latest_block.block_index if latest_block else None,
        'event_breakdown': event_breakdown
    }


def export_blockchain_proof(start_index=None, end_index=None):
    """
    Export blockchain data for external verification or legal evidence
    
    Args:
        start_index: Optional starting block index
        end_index: Optional ending block index
    
    Returns:
        dict: Complete blockchain data with verification info
    """
    query = BlockchainEventLog.query.order_by(BlockchainEventLog.block_index)
    
    if start_index is not None:
        query = query.filter(BlockchainEventLog.block_index >= start_index)
    if end_index is not None:
        query = query.filter(BlockchainEventLog.block_index <= end_index)
    
    blocks = query.all()
    
    is_valid, message, corrupted = verify_blockchain()
    
    return {
        'export_timestamp': datetime.utcnow().isoformat(),
        'total_blocks': len(blocks),
        'blockchain_verified': is_valid,
        'verification_message': message,
        'blocks': [
            {
                'block_index': block.block_index,
                'event_type': block.event_type,
                'description': block.description,
                'timestamp': block.timestamp.isoformat(),
                'block_hash': block.block_hash,
                'previous_hash': block.previous_hash,
                'user_id': block.user_id,
                'ip_address': block.ip_address
            }
            for block in blocks
        ],
        'cryptographic_signature': hashlib.sha256(
            json.dumps([b.block_hash for b in blocks]).encode()
        ).hexdigest()
    }


def get_block_by_hash(block_hash):
    """Find a block by its hash"""
    return BlockchainEventLog.query.filter_by(block_hash=block_hash).first()


def get_block_by_index(block_index):
    """Find a block by its index"""
    return BlockchainEventLog.query.filter_by(block_index=block_index).first()


def search_blockchain(event_type=None, description_contains=None, 
                     start_date=None, end_date=None, user_id=None):
    """
    Search blockchain events with filters
    
    Args:
        event_type: Filter by event type
        description_contains: Search description text
        start_date: Filter events after this date
        end_date: Filter events before this date
        user_id: Filter by user ID
    
    Returns:
        list: Matching blockchain events
    """
    query = BlockchainEventLog.query
    
    if event_type:
        query = query.filter_by(event_type=event_type)
    
    if description_contains:
        query = query.filter(BlockchainEventLog.description.contains(description_contains))
    
    if start_date:
        query = query.filter(BlockchainEventLog.timestamp >= start_date)
    
    if end_date:
        query = query.filter(BlockchainEventLog.timestamp <= end_date)
    
    if user_id:
        query = query.filter_by(user_id=user_id)
    
    return query.order_by(BlockchainEventLog.block_index).all()
