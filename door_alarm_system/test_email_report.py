#!/usr/bin/env python3
"""
Test script to manually send a scheduled report email
"""
import sys
from datetime import datetime, timedelta

# Add current directory to path
sys.path.insert(0, '/home/bsm/WebApp/eDOMOS-v2.1/door_alarm_system')

from app import app, db
from models import EmailConfig, ScheduledReport

def test_email_report():
    """Test sending a scheduled report via email"""
    
    with app.app_context():
        # Check email configuration
        email_config = EmailConfig.query.first()
        if not email_config or not email_config.is_configured:
            print("❌ Error: Email not configured in System Configuration")
            print("   Please configure email settings in the admin panel first")
            return False
        
        print("✅ Email configured:")
        print(f"   Sender: {email_config.sender_email}")
        print(f"   Recipients: {email_config.recipient_emails}")
        print()
        
        # Check for scheduled reports
        reports = ScheduledReport.query.all()
        
        if not reports:
            print("❌ No scheduled reports found")
            print("   Please create a scheduled report in Advanced Analytics first")
            return False
        
        print(f"📊 Found {len(reports)} scheduled report(s):")
        for idx, report in enumerate(reports, 1):
            print(f"   {idx}. Type: {report.report_type}, Frequency: {report.frequency}")
            print(f"      Recipients: {report.recipients}")
            print(f"      Enabled: {report.enabled}")
            print(f"      Next run: {report.next_run}")
        
        print()
        
        # Use the first report for testing
        report = reports[0]
        print(f"🧪 Testing email delivery for report: {report.report_type}")
        print()
        
        # Import required functions
        from app import generate_scheduled_report_pdf, send_scheduled_report_email
        
        # Generate date range
        now = datetime.now()
        if report.frequency == 'daily':
            start_date = (now - timedelta(days=1)).strftime('%Y-%m-%d')
            end_date = now.strftime('%Y-%m-%d')
        elif report.frequency == 'weekly':
            start_date = (now - timedelta(days=7)).strftime('%Y-%m-%d')
            end_date = now.strftime('%Y-%m-%d')
        elif report.frequency == 'monthly':
            start_date = (now - timedelta(days=30)).strftime('%Y-%m-%d')
            end_date = now.strftime('%Y-%m-%d')
        else:
            start_date = (now - timedelta(days=1)).strftime('%Y-%m-%d')
            end_date = now.strftime('%Y-%m-%d')
        
        print(f"📅 Report period: {start_date} to {end_date}")
        print()
        
        # Generate PDF
        print("📄 Generating PDF report...")
        import json
        filters = json.loads(report.filters) if report.filters else {}
        event_types = filters.get('event_types', ['door_open', 'door_close', 'alarm_triggered'])
        
        pdf_buffer = generate_scheduled_report_pdf(
            start_date=start_date,
            end_date=end_date,
            event_types=event_types,
            report_type=report.report_type
        )
        
        if not pdf_buffer:
            print("❌ Failed to generate PDF")
            return False
        
        print(f"✅ PDF generated: {len(pdf_buffer.getvalue())} bytes")
        print()
        
        # Send email
        print("📧 Sending email...")
        success = send_scheduled_report_email(
            report=report,
            pdf_buffer=pdf_buffer,
            start_date=start_date,
            end_date=end_date
        )
        
        if success:
            print()
            print("=" * 60)
            print("✅ EMAIL SENT SUCCESSFULLY!")
            print("=" * 60)
            print(f"📧 Recipients: {report.recipients}")
            print(f"📎 PDF attached: {len(pdf_buffer.getvalue())} bytes")
            print()
            print("💡 Tips:")
            print("   - Check your inbox (and spam/junk folder)")
            print("   - Email may take a few minutes to arrive")
            print("   - Verify sender email in System Configuration")
            return True
        else:
            print()
            print("=" * 60)
            print("❌ EMAIL SENDING FAILED")
            print("=" * 60)
            print()
            print("🔍 Troubleshooting steps:")
            print("   1. Check email configuration in System Configuration")
            print("   2. Verify Gmail app password is correct")
            print("   3. Enable 2-factor authentication on Gmail")
            print("   4. Generate new app password at: https://myaccount.google.com/apppasswords")
            print("   5. Check server logs: tail -f /tmp/edomos_https.log")
            return False

if __name__ == '__main__':
    print()
    print("=" * 60)
    print("🧪 eDOMOS SCHEDULED REPORT EMAIL TEST")
    print("=" * 60)
    print()
    
    try:
        test_email_report()
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    print()
