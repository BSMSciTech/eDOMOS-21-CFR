#!/usr/bin/env python3
"""
Create test users for multi-level approval testing
"""
import os
import sys
from werkzeug.security import generate_password_hash
import sqlite3

def create_test_users():
    """Create test users with different approval levels"""
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'alarm_system.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🔄 Creating test users for multi-level approval...")
    print("=" * 60)
    
    # Test users with different approval levels
    test_users = [
        {
            'username': 'user1',
            'password': 'user123',
            'full_name': 'Test User',
            'email': 'user1@test.com',
            'department': 'Operations',
            'role': 'Operator',
            'approval_level': 'user',
            'is_admin': False
        },
        {
            'username': 'supervisor1',
            'password': 'super123',
            'full_name': 'Supervisor One',
            'email': 'supervisor1@test.com',
            'department': 'Operations',
            'role': 'Supervisor',
            'approval_level': 'supervisor',
            'is_admin': False
        },
        {
            'username': 'manager1',
            'password': 'manager123',
            'full_name': 'Manager One',
            'email': 'manager1@test.com',
            'department': 'Quality Assurance',
            'role': 'QA Manager',
            'approval_level': 'manager',
            'is_admin': False
        },
        {
            'username': 'director1',
            'password': 'director123',
            'full_name': 'Director One',
            'email': 'director1@test.com',
            'department': 'Quality Assurance',
            'role': 'QA Director',
            'approval_level': 'director',
            'is_admin': False
        }
    ]
    
    # Check existing users
    for user in test_users:
        cursor.execute("SELECT id FROM user WHERE username = ?", (user['username'],))
        existing = cursor.fetchone()
        
        if existing:
            print(f"⚠️  User '{user['username']}' already exists - updating approval_level to {user['approval_level']}")
            cursor.execute(
                """UPDATE user 
                   SET approval_level = ?, 
                       full_name = ?,
                       email = ?,
                       department = ?,
                       role = ?
                   WHERE username = ?""",
                (user['approval_level'], user['full_name'], user['email'], 
                 user['department'], user['role'], user['username'])
            )
        else:
            print(f"✨ Creating user '{user['username']}' with approval level: {user['approval_level']}")
            password_hash = generate_password_hash(user['password'])
            
            cursor.execute(
                """INSERT INTO user 
                   (username, password_hash, full_name, email, department, role, 
                    approval_level, is_admin, is_active) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (user['username'], password_hash, user['full_name'], user['email'],
                 user['department'], user['role'], user['approval_level'],
                 user['is_admin'], True)
            )
    
    # Update admin user to have admin approval level
    print(f"✨ Updating admin user to admin approval level")
    cursor.execute("UPDATE user SET approval_level = 'admin' WHERE is_admin = 1")
    
    conn.commit()
    conn.close()
    
    print("=" * 60)
    print("✅ Test users created successfully!")
    print()
    print("Test User Credentials:")
    print("-" * 60)
    for user in test_users:
        print(f"  Username: {user['username']:15} Password: {user['password']:12} Level: {user['approval_level']}")
    print(f"  Username: {'admin':15} Password: {'admin123':12} Level: admin")
    print()
    print("Multi-Level Approval Workflow:")
    print("-" * 60)
    print("  1. user1 creates change request → Status: pending_supervisor")
    print("  2. supervisor1 approves → Status: pending_manager")
    print("  3. manager1 approves → Status: pending_director")
    print("  4. director1 approves → Status: pending_admin")
    print("  5. admin approves → Status: approved")
    print("  6. admin implements → Status: implemented")

if __name__ == '__main__':
    create_test_users()
