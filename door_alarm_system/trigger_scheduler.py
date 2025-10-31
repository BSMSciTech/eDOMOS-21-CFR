#!/usr/bin/env python3
"""Manually trigger scheduled report check and send"""

import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
from models import db, ScheduledReport, EventLog, EmailConfig
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import smtplib
import json
from io import BytesIO

# Import PDF libraries
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER

def generate_pdf(start_date, end_date, event_types, report_type):
    """Generate PDF report"""
    try:
        # Query events
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
        
        query = EventLog.query.filter(EventLog.timestamp.between(start_dt, end_dt))
        if event_types:
            query = query.filter(EventLog.event_type.in_(event_types))
        
        events = query.all()
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=A4,
            rightMargin=0.75*inch, leftMargin=0.75*inch,
            topMargin=1*inch, bottomMargin=1*inch
        )
        
        story = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'Title', parent=styles['Title'],
            fontSize=20, fontName='Helvetica-Bold',
            textColor=colors.HexColor('#0066CC'),
            spaceAfter=12, alignment=TA_CENTER
        )
        
        story.append(Paragraph(f"eDOMOS {report_type.title()} Report", title_style))
        story.append(Paragraph(f"Period: {start_date} to {end_date}", styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Summary
        summary_data = [
            ['Total Events:', str(len(events))],
            ['Report Type:', report_type.title()],
            ['Generated:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
        ]
        
        summary_table = Table(summary_data, colWidths=[2.5*inch, 3*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E3F2FD')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Events table
        if events:
            story.append(Paragraph("Event Details", styles['Heading2']))
            event_data = [['Date/Time', 'Event Type', 'Description']]
            
            for event in events[:100]:
                event_data.append([
                    event.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    event.event_type.replace('_', ' ').title(),
                    event.description or '-'
                ])
            
            event_table = Table(event_data, colWidths=[2*inch, 2*inch, 1.5*inch])
            event_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0066CC')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')])
            ]))
            
            story.append(event_table)
        
        doc.build(story)
        buffer.seek(0)
        
        print(f"   📄 PDF generated: {len(buffer.getvalue())} bytes, {len(events)} events")
        return buffer
        
    except Exception as e:
        print(f"   ❌ PDF generation failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def send_email(report, pdf_buffer, start_date, end_date):
    """Send email with PDF attachment"""
    try:
        email_config = EmailConfig.query.first()
        if not email_config:
            print("   ❌ No email configuration found")
            return False
        
        recipients = [email.strip() for email in report.recipients.split(',')]
        print(f"   📧 Preparing email for {len(recipients)} recipients: {recipients}")
        
        msg = MIMEMultipart()
        msg['From'] = email_config.sender_email
        msg['To'] = report.recipients
        msg['Subject'] = f"eDOMOS {report.report_type.title()} Report - {start_date} to {end_date}"
        
        body = f"""
📊 Scheduled {report.report_type.title()} Report

📅 Report Period: {start_date} to {end_date}
🔄 Frequency: {report.frequency.title()}
📧 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Please find the detailed report attached as a PDF file.

---
This is an automated email from eDOMOS Door Alarm System.
"""
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Attach PDF
        if pdf_buffer:
            pdf_attachment = MIMEApplication(pdf_buffer.read(), _subtype='pdf')
            pdf_attachment.add_header(
                'Content-Disposition', 'attachment',
                filename=f"eDOMOS_Report_{start_date}_to_{end_date}.pdf"
            )
            msg.attach(pdf_attachment)
            print(f"   📎 PDF attached: eDOMOS_Report_{start_date}_to_{end_date}.pdf ({len(pdf_buffer.getvalue())} bytes)")
        
        # Send email
        print("   📤 Connecting to Gmail SMTP...")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email_config.sender_email, email_config.app_password)
        
        print(f"   📤 Sending email to {len(recipients)} recipients...")
        server.sendmail(email_config.sender_email, recipients, msg.as_string())
        server.quit()
        
        print(f"   ✅ Email sent successfully to: {', '.join(recipients)}")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"   ❌ SMTP Authentication failed: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Email send failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function to check and send due reports"""
    from app import app
    
    with app.app_context():
        print("🔍 Checking for due scheduled reports...")
        
        now = datetime.now()
        print(f"⏰ Current time: {now.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Find all enabled reports that are due
        due_reports = ScheduledReport.query.filter(
            ScheduledReport.enabled == True,
            ScheduledReport.next_run <= now
        ).all()
        
        if not due_reports:
            print(f"📭 No reports due at this time")
            
            # Show next scheduled reports
            upcoming = ScheduledReport.query.filter(
                ScheduledReport.enabled == True
            ).order_by(ScheduledReport.next_run).limit(3).all()
            
            if upcoming:
                print(f"\n📅 Next {len(upcoming)} scheduled reports:")
                for r in upcoming:
                    print(f"   - Report #{r.id} at {r.next_run} ({r.report_type})")
            return
        
        print(f"\n📊 Found {len(due_reports)} report(s) due for sending:\n")
        
        for report in due_reports:
            print(f"{'='*70}")
            print(f"📄 Report #{report.id}: {report.report_type} ({report.frequency})")
            print(f"   Recipients: {report.recipients}")
            print(f"   Next Run: {report.next_run}")
            
            try:
                # Generate date range
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
                
                print(f"   Period: {start_date} to {end_date}")
                
                # Parse filters
                filters = json.loads(report.filters) if report.filters else {}
                event_types = filters.get('event_types', ['door_open', 'door_close', 'alarm_triggered'])
                
                # Generate PDF
                pdf_buffer = generate_pdf(start_date, end_date, event_types, report.report_type)
                
                if not pdf_buffer:
                    print("   ❌ Skipping email - PDF generation failed")
                    continue
                
                # Send email
                success = send_email(report, pdf_buffer, start_date, end_date)
                
                if success:
                    # Update report schedule
                    report.last_run = now
                    
                    # Parse scheduled time
                    scheduled_time = report.scheduled_time or '09:00'
                    hour, minute = map(int, scheduled_time.split(':'))
                    
                    # Calculate next run
                    if report.frequency == 'daily':
                        next_date = now.date() + timedelta(days=1)
                    elif report.frequency == 'weekly':
                        next_date = now.date() + timedelta(days=7)
                    elif report.frequency == 'monthly':
                        next_date = now.date() + timedelta(days=30)
                    else:
                        next_date = now.date() + timedelta(days=1)
                    
                    report.next_run = datetime.combine(next_date, datetime.min.time()).replace(hour=hour, minute=minute)
                    
                    db.session.commit()
                    print(f"   ✅ Report sent successfully!")
                    print(f"   📅 Next run scheduled for: {report.next_run}")
                
            except Exception as e:
                print(f"   ❌ Failed to process report: {e}")
                import traceback
                traceback.print_exc()
                db.session.rollback()
        
        print(f"\n{'='*70}")
        print("✅ Scheduler check complete!")

if __name__ == '__main__':
    main()
