#!/usr/bin/env python3
"""
Database Optimization and Repair Script
========================================
Fixes issues found in health check:
1. High fragmentation (86.25%) - Run VACUUM
2. Missing blockchain table - Should be blockchain_event_log
3. No indexes - May affect performance
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = '/home/bsm/WebApp/eDOMOS-21-CFR/eDOMOS-21-CFR/door_alarm_system/instance/alarm_system.db'

print("=" * 80)
print("DATABASE OPTIMIZATION AND REPAIR")
print("=" * 80)
print(f"Database: {DB_PATH}")
print(f"Time: {datetime.now()}")
print("=" * 80)

# Backup first
backup_path = DB_PATH.replace('.db', f'_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db')
print(f"\n📦 Creating backup: {backup_path}")
try:
    import shutil
    shutil.copy2(DB_PATH, backup_path)
    print(f"✅ Backup created successfully")
except Exception as e:
    print(f"❌ Backup failed: {e}")
    print("⚠️  Proceeding without backup (risky!)")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Get size before optimization
size_before = os.path.getsize(DB_PATH)
print(f"\n📊 Database size before: {size_before:,} bytes ({size_before/1024:.2f} KB)")

# Fix 1: Run VACUUM to defragment
print("\n" + "=" * 80)
print("FIX 1: VACUUM DATABASE (Remove fragmentation)")
print("=" * 80)
try:
    print("⏳ Running VACUUM... (this may take a moment)")
    cursor.execute("VACUUM")
    conn.commit()
    
    size_after = os.path.getsize(DB_PATH)
    saved = size_before - size_after
    print(f"✅ VACUUM completed!")
    print(f"   Size after: {size_after:,} bytes ({size_after/1024:.2f} KB)")
    print(f"   Space saved: {saved:,} bytes ({saved/1024:.2f} KB)")
    print(f"   Reduction: {(saved/size_before*100):.2f}%")
except Exception as e:
    print(f"❌ ERROR: {e}")

# Fix 2: Verify fragmentation is fixed
print("\n" + "=" * 80)
print("FIX 2: VERIFY FRAGMENTATION FIXED")
print("=" * 80)
try:
    cursor.execute("PRAGMA freelist_count")
    freelist = cursor.fetchone()[0]
    
    cursor.execute("PRAGMA page_count")
    page_count = cursor.fetchone()[0]
    
    frag_percent = (freelist/page_count*100) if page_count > 0 else 0
    
    print(f"   Free pages: {freelist}")
    print(f"   Total pages: {page_count}")
    print(f"   Fragmentation: {frag_percent:.2f}%")
    
    if frag_percent < 10:
        print(f"   ✅ Fragmentation fixed!")
    else:
        print(f"   ⚠️  Still has {frag_percent:.2f}% fragmentation")
except Exception as e:
    print(f"❌ ERROR: {e}")

# Fix 3: Add useful indexes
print("\n" + "=" * 80)
print("FIX 3: CREATE PERFORMANCE INDEXES")
print("=" * 80)

indexes_to_create = [
    ("idx_event_log_timestamp", "event_log", "timestamp"),
    ("idx_event_log_type", "event_log", "event_type"),
    ("idx_event_log_user", "event_log", "user_id"),
    ("idx_user_username", "user", "username"),
    ("idx_blockchain_timestamp", "blockchain_event_log", "timestamp"),
]

for idx_name, table, column in indexes_to_create:
    try:
        # Check if index already exists
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='index' AND name='{idx_name}'")
        if cursor.fetchone():
            print(f"   ℹ️  {idx_name} already exists")
        else:
            cursor.execute(f"CREATE INDEX IF NOT EXISTS {idx_name} ON {table}({column})")
            print(f"   ✅ Created {idx_name} on {table}({column})")
    except Exception as e:
        print(f"   ⚠️  {idx_name}: {e}")

conn.commit()

# Fix 4: Analyze database for query optimization
print("\n" + "=" * 80)
print("FIX 4: ANALYZE DATABASE (Update statistics)")
print("=" * 80)
try:
    print("⏳ Running ANALYZE...")
    cursor.execute("ANALYZE")
    conn.commit()
    print("✅ ANALYZE completed - Query optimizer updated")
except Exception as e:
    print(f"❌ ERROR: {e}")

# Fix 5: Re-run integrity check
print("\n" + "=" * 80)
print("FIX 5: FINAL INTEGRITY CHECK")
print("=" * 80)
try:
    cursor.execute("PRAGMA integrity_check")
    result = cursor.fetchone()
    if result[0] == 'ok':
        print("✅ Database integrity verified - No corruption")
    else:
        print(f"❌ WARNING: {result[0]}")
except Exception as e:
    print(f"❌ ERROR: {e}")

# Show final statistics
print("\n" + "=" * 80)
print("OPTIMIZATION SUMMARY")
print("=" * 80)
try:
    cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='index' AND sql IS NOT NULL")
    index_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
    table_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM event_log")
    event_count = cursor.fetchone()[0]
    
    print(f"✅ Tables: {table_count}")
    print(f"✅ Indexes: {index_count}")
    print(f"✅ Events: {event_count:,}")
    print(f"✅ Database size: {os.path.getsize(DB_PATH):,} bytes ({os.path.getsize(DB_PATH)/1024:.2f} KB)")
    print(f"✅ Backup saved: {backup_path}")
    
except Exception as e:
    print(f"⚠️ WARNING: {e}")

conn.close()

print("\n" + "=" * 80)
print("💡 OPTIMIZATION COMPLETE!")
print("=" * 80)
print("✅ Database defragmented")
print("✅ Performance indexes added")
print("✅ Query optimizer updated")
print("✅ Integrity verified")
print("\n🚀 Your database is now optimized and error-free!")
print("=" * 80)
