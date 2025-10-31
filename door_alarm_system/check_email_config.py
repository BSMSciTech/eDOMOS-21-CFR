#!/usr/bin/env python3
"""Check email configuration in database"""

import sqlite3

DB_PATH = 'instance/alarm_system.db'

try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check email configuration
    cursor.execute("SELECT id, sender_email, app_password, recipient_emails FROM email_config")
    config = cursor.fetchone()
    
    if config:
        config_id, sender, password, recipients = config
        print("📧 EMAIL CONFIGURATION:")
        print(f"   ├─ Sender Email: {sender}")
        print(f"   ├─ Password Set: {'✅ YES' if password else '❌ NO'}")
        print(f"   ├─ Password Length: {len(password) if password else 0} chars")
        print(f"   └─ Recipients: {recipients}")
        
        if sender and password:
            print("\n✅ Email configuration is COMPLETE")
        else:
            print("\n❌ Email configuration is INCOMPLETE")
    else:
        print("❌ No email configuration found")
    
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
