#!/usr/bin/env python3
"""
Quick test script for electronic signatures
Run this to verify the signature system works
"""

from app import app
from models import db, User, ElectronicSignature
import requests
import json

def test_signature_api():
    """Test signature creation via API"""
    
    print("=" * 70)
    print("ELECTRONIC SIGNATURE API TEST")
    print("=" * 70)
    print()
    
    # Test configuration
    BASE_URL = "http://localhost:5000"
    
    print("1. Testing if server is running...")
    try:
        response = requests.get(f"{BASE_URL}/login", timeout=2)
        print(f"   ✓ Server is running (Status: {response.status_code})")
    except Exception as e:
        print(f"   ✗ Server not running. Please start with: python3 app.py")
        print(f"   Error: {e}")
        return False
    
    print()
    print("2. Testing signature creation endpoint...")
    print("   Note: You must be logged in to test this via browser")
    print()
    
    # Test data
    test_signature = {
        "event_id": 9999,
        "event_type": "test",
        "action": "Test Electronic Signature from Script",
        "reason": "Testing the electronic signature API implementation",
        "password": "admin"  # Change this to your actual password
    }
    
    print("   Test payload:")
    print(f"   - Event ID: {test_signature['event_id']}")
    print(f"   - Event Type: {test_signature['event_type']}")
    print(f"   - Action: {test_signature['action']}")
    print(f"   - Reason: {test_signature['reason']}")
    print()
    
    print("=" * 70)
    print("MANUAL BROWSER TEST STEPS:")
    print("=" * 70)
    print()
    print("1. Open browser and navigate to:")
    print(f"   {BASE_URL}/login")
    print()
    print("2. Login with your credentials")
    print()
    print("3. Navigate to Electronic Signatures page:")
    print(f"   {BASE_URL}/electronic-signatures")
    print()
    print("4. Click any demo action card (e.g., 'Approve Change Control')")
    print()
    print("5. In the modal that opens:")
    print("   - Re-enter your password")
    print("   - Type a reason (at least 10 characters)")
    print("   - Click 'Sign Electronically'")
    print()
    print("6. You should see:")
    print("   - Success toast notification")
    print("   - Signature appears in the log on the right")
    print("   - Statistics update")
    print()
    print("=" * 70)
    
    return True

def test_database():
    """Test database structure"""
    
    with app.app_context():
        print()
        print("=" * 70)
        print("DATABASE TEST")
        print("=" * 70)
        print()
        
        # Check if table exists
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        
        if 'electronic_signature' in tables:
            print("✓ electronic_signature table exists")
            
            # Get columns
            columns = inspector.get_columns('electronic_signature')
            print(f"✓ Table has {len(columns)} columns:")
            for col in columns:
                print(f"   - {col['name']} ({col['type']})")
            
            print()
            
            # Count signatures
            count = db.session.query(ElectronicSignature).count()
            print(f"✓ Current signatures in database: {count}")
            
            if count > 0:
                # Show latest signature
                latest = db.session.query(ElectronicSignature)\
                    .order_by(ElectronicSignature.timestamp.desc())\
                    .first()
                print(f"\n  Latest signature:")
                print(f"  - ID: {latest.id}")
                print(f"  - User ID: {latest.user_id}")
                print(f"  - Action: {latest.action}")
                print(f"  - Timestamp: {latest.timestamp}")
                print(f"  - Hash: {latest.signature_hash[:32]}...")
            
        else:
            print("✗ electronic_signature table NOT found")
            print("   Run migration: python3 run_part11_migration.py")

def test_curl_examples():
    """Show curl examples for API testing"""
    
    print()
    print("=" * 70)
    print("CURL API TEST EXAMPLES")
    print("=" * 70)
    print()
    print("Note: You need to get a session cookie first by logging in")
    print()
    
    print("1. Login and get cookie:")
    print("""
    curl -c cookies.txt -X POST http://localhost:5000/login \\
      -d "username=admin&password=admin" \\
      -L
    """)
    
    print()
    print("2. Create signature:")
    print("""
    curl -b cookies.txt -X POST http://localhost:5000/api/signature/create \\
      -H "Content-Type: application/json" \\
      -d '{
        "event_id": 9999,
        "event_type": "test",
        "action": "Test signature from curl",
        "reason": "Testing the API with curl command",
        "password": "admin"
      }'
    """)
    
    print()
    print("3. Get user signatures:")
    print("""
    curl -b cookies.txt http://localhost:5000/api/signature/user/1?limit=5
    """)
    
    print()
    print("4. Verify specific signature:")
    print("""
    curl -b cookies.txt http://localhost:5000/api/signature/verify/1
    """)

def main():
    """Run all tests"""
    
    print("\n")
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║       ELECTRONIC SIGNATURE TEST GUIDE                            ║")
    print("║       21 CFR Part 11 Implementation                              ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    
    # Test API
    test_signature_api()
    
    # Test database
    test_database()
    
    # Show curl examples
    test_curl_examples()
    
    print()
    print("=" * 70)
    print("QUICK ACCESS URLs")
    print("=" * 70)
    print()
    print(f"Login:                http://localhost:5000/login")
    print(f"Dashboard:            http://localhost:5000/")
    print(f"E-Signatures:         http://localhost:5000/electronic-signatures")
    print(f"Blockchain:           http://localhost:5000/blockchain")
    print(f"Compliance:           http://localhost:5000/hipaa-compliance")
    print()
    print("=" * 70)
    print("TROUBLESHOOTING")
    print("=" * 70)
    print()
    print("Server not running?")
    print("  → python3 app.py")
    print()
    print("Table not found?")
    print("  → python3 run_part11_migration.py")
    print()
    print("Can't login?")
    print("  → Check username/password")
    print("  → Default: admin/admin")
    print()
    print("Modal doesn't open?")
    print("  → Check browser console (F12)")
    print("  → Verify signature-modal.js is loaded")
    print()
    print("API errors?")
    print("  → Check server logs")
    print("  → Verify you're logged in")
    print()
    print("=" * 70)
    print()

if __name__ == '__main__':
    main()
