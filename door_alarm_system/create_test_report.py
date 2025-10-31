#!/usr/bin/env python3
"""Create a test scheduled report to run in 3 minutes"""

import sqlite3
from datetime import datetime, timedelta

DB_PATH = 'instance/alarm_system.db'

try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Calculate time 3 minutes from now
    now = datetime.now()
    test_time = now + timedelta(minutes=3)
    scheduled_time = test_time.strftime('%H:%M')
    next_run = test_time.strftime('%Y-%m-%d %H:%M:%S.%f')
    
    print(f"⏰ Current time: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"⏰ Test report will run at: {test_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"⏰ Scheduled time: {scheduled_time}")
    
    # Insert test report
    cursor.execute("""
        INSERT INTO scheduled_report 
        (report_type, frequency, scheduled_time, recipients, enabled, 
         last_run, next_run, filters, created_by, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        'compliance_audit',
        'daily',
        scheduled_time,
        'srinivasmurthym@gmail.com',
        1,  # enabled
        None,  # last_run
        next_run,
        '{"event_types": ["door_open", "door_close", "alarm_triggered"]}',
        1,  # admin user
        now.strftime('%Y-%m-%d %H:%M:%S.%f'),
        now.strftime('%Y-%m-%d %H:%M:%S.%f')
    ))
    
    conn.commit()
    report_id = cursor.lastrowid
    
    print(f"\n✅ Test report created successfully!")
    print(f"📄 Report ID: {report_id}")
    print(f"📧 Recipient: srinivasmurthym@gmail.com")
    print(f"⏰ Will send in ~3 minutes at: {test_time.strftime('%H:%M:%S')}")
    print(f"\n📋 The scheduler checks every hour, but since this is due, it should")
    print(f"   send on the next scheduler check cycle.")
    print(f"\nℹ️  Watch the server logs for:")
    print(f"   [SCHEDULER] 📊 Processing scheduled report...")
    print(f"   [SCHEDULER] 📧 Preparing email...")
    print(f"   [SCHEDULER] ✅ Report sent successfully...")
    
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
