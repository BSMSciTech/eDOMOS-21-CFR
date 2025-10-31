# Time Settings Configuration Guide

## Overview
The eDOMOS system now supports configurable time settings for both anomaly detection and scheduled reports.

## Features Added

### 1. Anomaly Detection Business Hours
Configure when door access is considered "normal" to detect odd-hours anomalies.

**Location**: Admin Panel → Settings → Anomaly Detection Settings

**Settings**:
- **Business Hours Start**: Start of normal working hours (default: 09:00)
- **Business Hours End**: End of normal working hours (default: 17:00)

**How it works**:
- Door access outside these hours triggers an "odd_hours" anomaly
- Anomalies are logged with medium severity
- Visible in Advanced Analytics → Anomalies tab

**Example**:
- Set business hours: 08:00 - 18:00
- If door opens at 07:30 or 19:00 → Anomaly detected

---

### 2. Scheduled Report Time
Set specific time when reports should be sent automatically.

**Location**: Advanced Analytics → Scheduled Reports → Create Schedule

**Settings**:
- **Scheduled Time**: Time to send report (HH:MM format, 24-hour)
- **Frequency**: Daily, Weekly, or Monthly
- **Report Type**: Summary or Compliance Audit
- **Recipients**: Comma-separated email addresses

**How it works**:
- Reports are generated and emailed at the specified time
- Next run is calculated based on frequency + scheduled time
- Scheduler checks every hour for due reports

**Example**:
```
Report Type: Compliance Audit
Frequency: Daily
Scheduled Time: 09:00
Recipients: admin@example.com

Result: Report sent every day at 9:00 AM
```

---

## Configuration Steps

### Step 1: Set Business Hours (Anomaly Detection)

1. Login as admin
2. Navigate to **Settings → System Configuration**
3. Find **Anomaly Detection Settings** card
4. Set **Business Hours Start** (e.g., 08:00)
5. Set **Business Hours End** (e.g., 18:00)
6. Click **Save Anomaly Settings**

**Database Update**:
```sql
INSERT INTO setting (key, value) VALUES 
  ('business_hours_start', '8'),
  ('business_hours_end', '18');
```

---

### Step 2: Create Scheduled Report with Time

1. Login as admin
2. Navigate to **Advanced Analytics**
3. Click **Scheduled Reports** tab
4. Click **Create Schedule** button
5. Fill in the form:
   - Report Type: Summary or Compliance Audit
   - Frequency: Daily/Weekly/Monthly
   - **Scheduled Time**: Select time (e.g., 09:00)
   - Recipients: Enter email addresses
6. Click **Create**

**API Call Example**:
```javascript
POST /api/scheduled-reports
{
  "report_type": "compliance_audit",
  "frequency": "daily",
  "scheduled_time": "09:00",
  "recipients": "admin@example.com"
}
```

---

## Database Schema

### ScheduledReport Model (Updated)
```python
class ScheduledReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    report_type = db.Column(db.String(50))
    frequency = db.Column(db.String(20))
    scheduled_time = db.Column(db.String(5), default='09:00')  # NEW FIELD
    recipients = db.Column(db.Text)
    enabled = db.Column(db.Boolean, default=True)
    next_run = db.Column(db.DateTime)
    # ... other fields
```

### Settings Table
```sql
CREATE TABLE setting (
    id INTEGER PRIMARY KEY,
    key VARCHAR(50) UNIQUE,
    value TEXT
);

-- Anomaly detection settings
INSERT INTO setting (key, value) VALUES ('business_hours_start', '9');
INSERT INTO setting (key, value) VALUES ('business_hours_end', '17');
```

---

## How Next Run is Calculated

### Scheduler Logic
```python
# Parse scheduled time (HH:MM)
hour, minute = map(int, scheduled_time.split(':'))

# Calculate next date based on frequency
if frequency == 'daily':
    next_date = now.date() + timedelta(days=1)
elif frequency == 'weekly':
    next_date = now.date() + timedelta(days=7)
elif frequency == 'monthly':
    next_date = now.date() + timedelta(days=30)

# Combine date with scheduled time
next_run = datetime.combine(next_date, datetime.min.time())
next_run = next_run.replace(hour=hour, minute=minute)
```

**Example**:
```
Current time: 2025-10-26 14:30
Frequency: Daily
Scheduled Time: 09:00

→ Next run: 2025-10-27 09:00
```

---

## Testing

### Test Anomaly Detection
```bash
# 1. Set business hours to 09:00 - 17:00
# 2. Access door at 08:00 or 19:00
# 3. Check Advanced Analytics → Anomalies tab
# Expected: "odd_hours" anomaly with description
```

### Test Scheduled Reports
```bash
cd /home/bsm/WebApp/eDOMOS-v2.1/door_alarm_system
python test_email_report.py
```

Expected output:
```
📧 Sending email...
[SCHEDULER] 📧 Preparing email for 1 recipients: ['admin@example.com']
[SCHEDULER] 📎 PDF attached: eDOMOS_Report_2025-10-25_to_2025-10-26.pdf (2880 bytes)
[SCHEDULER] 🔗 Connecting to SMTP server (smtp.gmail.com:587)...
[SCHEDULER] ✅ Report emailed successfully to 1 recipients
```

---

## Troubleshooting

### Issue: Anomalies not detected at odd hours

**Solution**:
1. Check business hours settings in Admin Panel
2. Verify settings are saved in database:
```sql
SELECT * FROM setting WHERE key LIKE 'business_hours%';
```
3. Restart server to apply changes

---

### Issue: Reports not sent at scheduled time

**Possible Causes**:
1. Email not configured
2. Scheduled time format incorrect
3. Report scheduler thread not running

**Solution**:
```bash
# Check logs for scheduler activity
tail -f /tmp/edomos_https.log | grep SCHEDULER

# Expected output every hour:
[SCHEDULER] 📧 Report scheduler thread started
```

---

### Issue: Next run time incorrect

**Solution**:
1. Delete and recreate the scheduled report with correct time
2. Verify scheduled_time field in database:
```sql
SELECT id, report_type, frequency, scheduled_time, next_run 
FROM scheduled_report;
```

---

## API Reference

### Get Scheduled Reports
```
GET /api/scheduled-reports
Authorization: Required (Admin only)

Response:
{
  "success": true,
  "reports": [
    {
      "id": 1,
      "report_type": "compliance_audit",
      "frequency": "daily",
      "scheduled_time": "09:00",
      "recipients": "admin@example.com",
      "next_run": "2025-10-27 09:00:00",
      "enabled": true
    }
  ]
}
```

### Create Scheduled Report
```
POST /api/scheduled-reports
Authorization: Required (Admin only)
Content-Type: application/json

{
  "report_type": "summary",
  "frequency": "daily",
  "scheduled_time": "09:00",
  "recipients": "admin@example.com"
}

Response:
{
  "success": true,
  "message": "Scheduled report created",
  "report": { ... }
}
```

### Get Anomaly Statistics
```
GET /api/anomalies/stats
Authorization: Required

Response:
{
  "success": true,
  "total_anomalies": 15,
  "unacknowledged": 3,
  "by_type": {
    "odd_hours": 8,
    "repeated_opens": 5,
    "prolonged_open": 2
  }
}
```

---

## Best Practices

1. **Business Hours**:
   - Set based on your organization's working hours
   - Consider timezone when setting hours
   - Update during daylight saving time changes

2. **Scheduled Reports**:
   - Choose off-peak hours for report generation (e.g., 02:00)
   - Or choose business start time (e.g., 08:00)
   - Ensure recipients are correct before enabling

3. **Email Delivery**:
   - Use valid Gmail app password
   - Check spam folders initially
   - Whitelist sender email in recipient systems

---

## Summary

✅ **Anomaly Detection**: Configure business hours in Admin Panel
✅ **Scheduled Reports**: Set delivery time when creating schedule
✅ **Next Run**: Automatically calculated based on frequency + time
✅ **Testing**: Use test_email_report.py for verification
✅ **Monitoring**: Check logs with `grep SCHEDULER`

For questions or issues, check server logs at `/tmp/edomos_https.log`
