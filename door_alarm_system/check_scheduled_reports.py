#!/usr/bin/env python3
"""Check scheduled reports in the database"""

import sqlite3
import os
from datetime import datetime

# Database path
DB_PATH = 'instance/alarm_system.db'

def check_reports():
    """Check all scheduled reports"""
    
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found: {DB_PATH}")
        return
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get all scheduled reports
        cursor.execute("""
            SELECT id, report_type, frequency, scheduled_time, recipients, 
                   enabled, last_run, next_run, created_at
            FROM scheduled_report
            ORDER BY id DESC
        """)
        
        reports = cursor.fetchall()
        
        if not reports:
            print("📭 No scheduled reports found in database")
            return
        
        print(f"\n📊 SCHEDULED REPORTS ({len(reports)} total)")
        print("=" * 100)
        
        for report in reports:
            report_id, report_type, frequency, scheduled_time, recipients, \
            enabled, last_run, next_run, created_at = report
            
            print(f"\n📄 Report ID: {report_id}")
            print(f"   ├─ Type: {report_type}")
            print(f"   ├─ Frequency: {frequency}")
            print(f"   ├─ Scheduled Time: {scheduled_time}")
            print(f"   ├─ Recipients: {recipients}")
            print(f"   ├─ Enabled: {'✅ YES' if enabled else '❌ NO'}")
            print(f"   ├─ Last Run: {last_run or 'Never'}")
            print(f"   ├─ Next Run: {next_run}")
            print(f"   └─ Created: {created_at}")
        
        # Check if any reports are due now
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute("""
            SELECT id, report_type, next_run, recipients
            FROM scheduled_report
            WHERE enabled = 1 AND next_run <= ?
        """, (now,))
        
        due_reports = cursor.fetchall()
        
        if due_reports:
            print(f"\n⏰ REPORTS DUE NOW ({len(due_reports)} found):")
            for report_id, report_type, next_run, recipients in due_reports:
                print(f"   - Report #{report_id} ({report_type}) for {recipients}")
                print(f"     Was due: {next_run}")
        else:
            print(f"\n✅ No reports currently due (checked against {now})")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return

if __name__ == '__main__':
    check_reports()
