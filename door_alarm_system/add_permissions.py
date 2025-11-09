#!/usr/bin/env python3
"""
Add missing permissions to admin user
"""
import sqlite3

# Connect to database
conn = sqlite3.connect('door_system.db')
cursor = conn.cursor()

# Get admin user
cursor.execute("SELECT id, username, permissions FROM user WHERE username = 'admin'")
result = cursor.fetchone()

if result:
    user_id, username, current_permissions = result
    print(f"Found user: {username} (ID: {user_id})")
    print(f"Current permissions: '{current_permissions}'")
    
    # Parse permissions
    perms = current_permissions.split(',') if current_permissions else []
    print(f"\nCurrent permission list:")
    for p in perms:
        print(f"  - {p}")
    
    # Check for missing permissions
    missing = []
    if 'event_log' not in perms:
        missing.append('event_log')
    if 'analytics' not in perms:
        missing.append('analytics')
    
    if missing:
        print(f"\n⚠️ Missing permissions: {', '.join(missing)}")
        
        # Add missing permissions
        perms.extend(missing)
        new_permissions = ','.join(perms)
        
        cursor.execute("UPDATE user SET permissions = ? WHERE id = ?", (new_permissions, user_id))
        conn.commit()
        
        print(f"✅ Updated permissions: '{new_permissions}'")
        print("\nNew permission list:")
        for p in perms:
            print(f"  - {p}")
    else:
        print("\n✅ All required permissions are already present!")
else:
    print("❌ Admin user not found!")

conn.close()
