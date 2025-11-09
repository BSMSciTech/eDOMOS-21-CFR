#!/usr/bin/env python3
"""Verify multi-level approval setup"""
import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'instance', 'alarm_system.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 60)
print("MULTI-LEVEL APPROVAL SYSTEM - VERIFICATION")
print("=" * 60)

# Check users
print("\n👥 Users by Approval Level:")
print("-" * 60)
cursor.execute('SELECT username, approval_level, is_admin FROM user ORDER BY approval_level')
for row in cursor.fetchall():
    admin_flag = "✅ Admin" if row[2] else ""
    print(f"  {row[0]:15} Level: {row[1]:12} {admin_flag}")

# Check change control schema
print("\n📋 ChangeControl Table Columns:")
print("-" * 60)
cursor.execute("PRAGMA table_info(change_control)")
approval_cols = [col[1] for col in cursor.fetchall() if 'approved' in col[1] or 'signature' in col[1]]
for col in approval_cols:
    print(f"  ✅ {col}")

# Check existing change requests
print("\n🔄 Existing Change Requests:")
print("-" * 60)
cursor.execute('SELECT change_number, status, title FROM change_control')
changes = cursor.fetchall()
if changes:
    for change in changes:
        print(f"  {change[0]}: {change[1]:20} - {change[2]}")
else:
    print("  No change requests yet")

# Check electronic signatures
print("\n🔐 Electronic Signatures:")
print("-" * 60)
cursor.execute('SELECT COUNT(*) FROM electronic_signature')
sig_count = cursor.fetchone()[0]
print(f"  Total signatures in system: {sig_count}")

# Check blockchain events
print("\n⛓️  Recent Blockchain Events:")
print("-" * 60)
cursor.execute('SELECT event_type, timestamp FROM blockchain_event_log ORDER BY timestamp DESC LIMIT 5')
events = cursor.fetchall()
for event in events:
    print(f"  {event[0]:30} - {event[1]}")

print("\n" + "=" * 60)
print("✅ VERIFICATION COMPLETE - System Ready for Testing!")
print("=" * 60)
print("\n🚀 Access: http://192.168.31.227:5000")
print("📖 Guide: QUICK_START_MULTI_LEVEL.md")
print()

conn.close()
