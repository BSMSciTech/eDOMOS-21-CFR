# eDOMOS License System Guide

## Overview

The eDOMOS license system allows you to control:
- **Number of Users** - Limit active user accounts
- **Number of Doors** - Limit door monitoring instances
- **Feature Access** - Enable/disable premium features
- **License Duration** - Time-based or lifetime licenses

---

## License Tiers

### 1. STARTER ($499)
```
Max Users: 2
Max Doors: 1
Features:
  ✗ Anomaly Detection
  ✗ PDF Reports
  ✗ Scheduled Reports
  ✗ API Access
```

### 2. PROFESSIONAL ($1,499)
```
Max Users: 10
Max Doors: 5
Features:
  ✓ Anomaly Detection
  ✓ PDF Reports
  ✓ Scheduled Reports
  ✗ API Access
```

### 3. ENTERPRISE ($3,999)
```
Max Users: 50
Max Doors: 20
Features:
  ✓ Anomaly Detection
  ✓ PDF Reports
  ✓ Scheduled Reports
  ✓ API Access
```

### 4. CUSTOM (Quote-based)
```
Max Users: Unlimited
Max Doors: Unlimited
Features: All enabled
```

---

## Setup Instructions

### Step 1: Install License System

Run the migration to create the License table:

```bash
python license_migration.py
```

This creates:
- License database table
- A default Professional license for testing

### Step 2: Generate Customer Licenses

#### Professional License (Lifetime):
```bash
python generate_license.py \
  --type professional \
  --customer "Acme Corp" \
  --email "admin@acmecorp.com" \
  --company "Acme Corporation"
```

#### Starter License (1 Year):
```bash
python generate_license.py \
  --type starter \
  --customer "Small Business LLC" \
  --email "owner@smallbiz.com" \
  --duration-days 365
```

#### Enterprise License (3 Years):
```bash
python generate_license.py \
  --type enterprise \
  --customer "Big Enterprise Inc" \
  --email "it@bigent.com" \
  --company "Big Enterprise Inc" \
  --duration-days 1095
```

#### Custom License:
```bash
python generate_license.py \
  --type custom \
  --customer "Special Customer" \
  --email "contact@special.com" \
  --max-users 100 \
  --max-doors 50 \
  --duration-days 730
```

---

## How Restrictions Work

### User Limits

When creating a new user, the system checks:
1. Is there an active license?
2. Is the license valid (not expired)?
3. Current user count < max_users?

If any check fails, user creation is blocked with an error message.

**Example Error:**
```
"License limit reached: 10 users maximum (Type: professional)"
```

### Door Limits

When adding a new door system:
1. Is there an active license?
2. Is the license valid?
3. Current door count < max_doors?

**Example Error:**
```
"License limit reached: 5 door(s) maximum (Type: professional)"
```

### Feature Restrictions

Premium features check if they're enabled:

```python
# Anomaly Detection
if not license.anomaly_detection_enabled:
    return "Feature disabled - Upgrade to Professional"

# PDF Reports
if not license.pdf_reports_enabled:
    return "Feature disabled - Upgrade to Professional"

# Scheduled Reports
if not license.scheduled_reports_enabled:
    return "Feature disabled - Upgrade to Professional"

# API Access
if not license.api_access_enabled:
    return "Feature disabled - Upgrade to Enterprise"
```

---

## Integration with Your App

### Check License Before Adding Users

In your user creation endpoint (app.py):

```python
from license_helper import can_add_user

@app.route('/api/users', methods=['POST'])
def create_user():
    # Check license first
    can_add, message = can_add_user()
    if not can_add:
        return jsonify({'success': False, 'error': message}), 403
    
    # Proceed with user creation
    # ... existing code ...
```

### Check License Before Adding Doors

In your door system creation:

```python
from license_helper import can_add_door

@app.route('/api/doors', methods=['POST'])
def create_door():
    # Check license first
    can_add, message = can_add_door()
    if not can_add:
        return jsonify({'success': False, 'error': message}), 403
    
    # Proceed with door creation
    # ... existing code ...
```

### Protect Feature Routes

```python
from license_helper import require_feature

@app.route('/api/anomalies')
@require_feature('anomaly_detection')
def get_anomalies():
    # Feature automatically blocked if not enabled in license
    # ... existing code ...
```

### Display License Info in Admin Panel

```python
from license_helper import get_license_info

@app.route('/admin/license')
def license_status():
    license_info = get_license_info()
    return render_template('license_info.html', license=license_info)
```

---

## License Management

### View Current License

```python
from license_helper import get_license_info

info = get_license_info()
print(f"Type: {info['license_type']}")
print(f"Users: {info['current_users']}/{info['max_users']}")
print(f"Doors: {info['current_doors']}/{info['max_doors']}")
print(f"Status: {info['status']}")
```

### Deactivate a License

```python
from models import License, db

license = License.query.filter_by(license_key='EDOMOS-PRO-XXXXX').first()
license.is_active = False
db.session.commit()
```

### Extend License

```python
from models import License, db
from datetime import date, timedelta

license = License.query.filter_by(license_key='EDOMOS-PRO-XXXXX').first()
license.expiration_date = date.today() + timedelta(days=365)
db.session.commit()
```

### Upgrade License

```python
from models import License, db

license = License.query.first()
license.license_type = 'enterprise'
license.max_users = 50
license.max_doors = 20
license.api_access_enabled = True
db.session.commit()
```

---

## Customer Deployment Process

### For You (Vendor):

1. **Customer Purchases License**
   - Customer selects tier (Starter/Pro/Enterprise)
   - Payment processed

2. **Generate License Key**
   ```bash
   python generate_license.py --type professional --customer "Customer Name" --email "their@email.com"
   ```

3. **Send License Key to Customer**
   - Email: "Your eDOMOS License Key: EDOMOS-PRO-XXXXXXXXXXXX"
   - Include installation instructions

### For Customer:

1. **Install eDOMOS Software**
   - Follow normal installation procedure

2. **Activate License** (future feature)
   - Enter license key in admin panel
   - System validates and activates

3. **System is Now Licensed**
   - Features enabled based on tier
   - Limits enforced automatically

---

## Multi-Door Support

Yes! Your current system **already supports multiple doors**:

### Current Architecture:

```python
# DoorSystemInfo table can have multiple entries
Door 1: Main Entrance (device_serial: DEV001)
Door 2: Back Door (device_serial: DEV002)
Door 3: Server Room (device_serial: DEV003)
Door 4: Warehouse (device_serial: DEV004)
Door 5: Emergency Exit (device_serial: DEV005)
```

### Each Door Can Have:
- Unique location/name
- Department assignment
- Serial number
- Separate event logging
- Individual status tracking

### How to Add More Doors:

**Option A: Same Hardware, Multiple Doors**
- One Raspberry Pi can monitor multiple doors using different GPIO pins
- Each door gets its own database entry

**Option B: Multiple Hardware Units**
- Each location has its own Raspberry Pi
- All connect to central eDOMOS database
- Unified monitoring dashboard

**Option C: Hybrid**
- Critical doors: Dedicated hardware
- Non-critical doors: Shared hardware
- All in one system

---

## Pricing Strategy with Licensing

### Per Door Pricing Model:

**Option 1: Tier-Based**
- Starter: 1 door included, $199/door additional
- Professional: 5 doors included, $149/door additional
- Enterprise: 20 doors included, $99/door additional

**Option 2: Door Packs**
- 1-5 doors: $1,499 (Professional)
- 6-10 doors: $2,499
- 11-20 doors: $3,999 (Enterprise)
- 21+ doors: Custom quote

**Option 3: Subscription Per Door**
- $29/month per door (Starter features)
- $49/month per door (Professional features)
- $79/month per door (Enterprise features)

---

## Revenue Examples

### Example 1: Small Warehouse (3 Doors)
```
Professional License: $1,499
3 Doors included (5 max)
Annual Support: $299
Total Year 1: $1,798
```

### Example 2: Multi-Location Retail (15 Doors)
```
Enterprise License: $3,999
20 Doors included
Annual Support: $799
Total Year 1: $4,798

Traditional System Cost: $45,000+
Your Savings to Customer: $40,000+ (89% savings!)
```

### Example 3: Large Facility (50 Doors)
```
Custom License: $12,000
50 Doors unlimited users
Premium Support: $2,000/year
Installation Service: $5,000
Total Year 1: $19,000

Traditional System: $150,000+
Your Savings to Customer: $131,000 (87% savings!)
```

---

## FAQ

### Q: Can customers bypass the license restrictions?
**A:** Yes, if they have access to the database or source code. For production:
- Use encrypted license keys
- Add license server validation
- Obfuscate license checks
- Use compiled Python (.pyc)

### Q: How do I handle license renewals?
**A:** Set expiration dates and send reminder emails:
- 90 days before: "Renewal coming up"
- 30 days before: "Renew now for uninterrupted service"
- At expiration: System switches to read-only mode

### Q: Can I offer trial licenses?
**A:** Yes! Generate 30-day licenses:
```bash
python generate_license.py --type professional --customer "Trial User" --email "trial@example.com" --duration-days 30
```

### Q: What happens when license expires?
**A:** Options:
1. **Grace Period**: 7 days warning, then disable features
2. **Read-Only Mode**: Can view data but not add users/doors
3. **Complete Lock**: System requires renewal to function

### Q: Can I transfer a license to another customer?
**A:** Yes, update the customer info in database:
```python
license.customer_name = "New Customer"
license.customer_email = "new@email.com"
db.session.commit()
```

---

## Next Steps

1. ✅ Run `python license_migration.py` to set up licensing
2. ✅ Test with default license
3. ✅ Integrate license checks into user/door creation
4. ✅ Add license info display in admin panel
5. ✅ Create customer licenses before deployment
6. ⏭️ Build web-based license activation UI
7. ⏭️ Add license renewal reminders
8. ⏭️ Create customer portal for license management

---

## Support

For license issues:
- Check license status: `get_license_info()`
- Validate license: `validate_license()`
- Contact vendor for renewals/upgrades
