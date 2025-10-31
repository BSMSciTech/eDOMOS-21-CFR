# eDOMOS v2.1 - Customization & Profile Management
## Complete System Configuration Guide

### 📅 **Implementation Date**: October 21, 2025
### 🎯 **Feature Version**: 1.0 - Complete Profile System

---

## 🌟 **OVERVIEW**

This comprehensive customization system allows administrators to configure:
- **Company Profile** (branding, logo, address)
- **Door & System Information** (location, department, serial number)
- **User Profiles** (full details, department, role, access)

All information is:
- ✅ Displayed on dashboards
- ✅ Included in PDF/CSV/JSON reports
- ✅ Collected during user onboarding
- ✅ Editable by administrators

---

## 📊 **DATABASE SCHEMA**

### **1. Enhanced User Model**

```python
class User:
    # Existing fields
    id, username, password_hash, is_admin, permissions
    
    # NEW Extended Profile Fields
    full_name              # Full legal name
    employee_id            # Unique employee identifier (EMP0001)
    department             # Department name
    role                   # Job role/title
    email                  # Contact email
    phone                  # Contact phone
    created_at             # Account creation timestamp
    last_login             # Last login timestamp
    is_active              # Account active status
```

### **2. CompanyProfile Model** (NEW)

```python
class CompanyProfile:
    id                     # Primary key
    company_name           # Organization name *
    company_address        # Street address
    company_city           # City
    company_state          # State/Province
    company_zip            # ZIP/Postal code
    company_country        # Country
    company_phone          # Contact phone
    company_email          # Contact email
    company_website        # Website URL
    company_logo_path      # Path to logo image
    updated_at             # Last update timestamp
```

### **3. DoorSystemInfo Model** (NEW)

```python
class DoorSystemInfo:
    id                     # Primary key
    door_location          # Physical location *
    department_name        # Responsible department *
    device_serial_number   # Unique device ID (EDOMOS-001) *
    system_model           # Model (eDOMOS v2.1)
    installation_date      # Installation date
    last_maintenance_date  # Last service date
    notes                  # Additional information
    is_active              # System active status
    updated_at             # Last update timestamp
```

---

## 🚀 **INSTALLATION & MIGRATION**

### **Step 1: Run Database Migration**

```bash
cd /home/bsm/WebApp/eDOMOS-v2.1/door_alarm_system

# Run migration script
python migrate_database.py
```

**What it does:**
- ✅ Adds new columns to `user` table
- ✅ Creates `company_profile` table
- ✅ Creates `door_system_info` table
- ✅ Initializes default values
- ✅ Updates existing users with default profile data

**Expected Output:**
```
====================================================================
eDOMOS v2.1 - Database Migration Tool
====================================================================

📊 Checking current database structure...
✓ Found 5 existing tables: user, setting, event_log, email_config, ...

👤 Migrating User table...
  ✓ Added column: user.full_name
  ✓ Added column: user.employee_id
  ✓ Added column: user.department
  ...

🏢 Creating CompanyProfile table...
  ✓ CompanyProfile table created successfully
  ✓ Default company profile initialized

🚪 Creating DoorSystemInfo table...
  ✓ DoorSystemInfo table created successfully
  ✓ Default door/system info initialized

✅ MIGRATION SUMMARY:
  ✓ user: 13 columns
  ✓ company_profile: 12 columns
  ✓ door_system_info: 10 columns

🎉 Database migration completed successfully!
```

### **Step 2: Verify Migration**

```bash
# Check tables exist
sqlite3 instance/edomos.db ".tables"

# Should show: company_profile, door_system_info, email_config, event_log, setting, user

# Check user table structure
sqlite3 instance/edomos.db ".schema user"
```

---

## 🎨 **ADMIN INTERFACE**

### **1. Company Profile Settings**

**Access:** Admin Menu → Company Profile

**Features:**
- Company information form
- Address fields (city, state, zip, country)
- Contact details (phone, email, website)
- Logo upload (PNG, JPG, SVG - max 2MB)
- Live logo preview
- Auto-save functionality

**API Endpoints:**
```
GET  /api/company-profile      - Retrieve company info
POST /api/company-profile      - Update company info
POST /api/upload-logo          - Upload company logo
```

### **2. Door & System Information**

**Access:** Company Profile page (bottom section)

**Fields:**
- **Door Location** * (e.g., "Main Entrance", "Building A")
- **Department Name** * (e.g., "Quality Control", "Production", "Stores")
- **Device Serial Number** * (e.g., "EDOMOS-001")
- **System Model** (Read-only: "eDOMOS v2.1")
- **Installation Date** (Optional)
- **Last Maintenance Date** (Optional)
- **Notes** (Optional - Additional information)

**API Endpoints:**
```
GET  /api/door-system-info     - Retrieve door/system info
POST /api/door-system-info     - Update door/system info
```

### **3. User Management**

**Access:** Admin Menu → User Management

**Features:**
- View all users in table format
- Add new user with complete profile
- Edit existing user profiles
- Delete users
- Toggle admin/active status

**User Profile Fields:**
- Username (unique) *
- Password (for new users) *
- Full Name *
- Employee ID * (unique)
- Department * (dropdown selection)
- Role * (dropdown selection)
- Email (optional)
- Phone (optional)
- Administrator Access (checkbox)
- Active Account (checkbox)

**Predefined Departments:**
- Quality Control
- Production
- Stores
- Security
- Administration
- IT
- HR
- Other

**Predefined Roles:**
- Operator
- Supervisor
- Manager
- Administrator
- Auditor

**API Endpoints:**
```
GET    /api/users              - List all users
POST   /api/users              - Create new user
GET    /api/users/:id          - Get user details
PUT    /api/users/:id          - Update user
DELETE /api/users/:id          - Delete user
```

---

## 📄 **REPORT INTEGRATION**

### **PDF Reports**

All customization information is automatically included in PDF reports:

**Header Section:**
```
┌─────────────────────────────────────────────────┐
│  [COMPANY LOGO]                                 │
│  COMPANY NAME                                   │
│  Address Line                                   │
│  City, State ZIP, Country                       │
│  Phone: xxx | Email: xxx                        │
└─────────────────────────────────────────────────┘

eDOMOS – DOOR MONITORING SYSTEM
Security Event Report

Door Location: Main Entrance
Department: Quality Control
Device S/N: EDOMOS-001
System Model: eDOMOS v2.1
```

**Footer Section:**
```
Generated by: John Smith (EMP0001)
Department: Security
Role: System Administrator
Report Date: October 21, 2025 03:45 PM

Company Name | Door Location: Main Entrance
Page 1 of 5
```

### **CSV Reports**

CSV exports include additional columns:

```csv
ID,Date,Time,Event Type,Status,User,Employee ID,Department,Door Location,Device S/N
1,2025-10-21,14:30:15,Door Open,OPEN,John Smith,EMP0001,Security,Main Entrance,EDOMOS-001
```

### **JSON Reports**

JSON exports include nested profile data:

```json
{
  "report_metadata": {
    "company": {
      "name": "Your Company Name",
      "address": "123 Main Street, City, State",
      "phone": "+1-234-567-8900"
    },
    "system": {
      "door_location": "Main Entrance",
      "department": "Quality Control",
      "device_serial": "EDOMOS-001",
      "model": "eDOMOS v2.1"
    },
    "generated_by": {
      "user": "John Smith",
      "employee_id": "EMP0001",
      "department": "Security",
      "role": "System Administrator"
    }
  },
  "events": [...]
}
```

---

## 🎯 **DASHBOARD INTEGRATION**

### **Hero Section**

```html
┌─────────────────────────────────────────────────┐
│  [LOGO]  COMPANY NAME                           │
│  Main Entrance - Quality Control Dept           │
│  Device: EDOMOS-001                             │
│                                                  │
│  Welcome back, John Smith (Security Dept)       │
└─────────────────────────────────────────────────┘
```

### **User Profile Widget**

```html
┌─────────────────────────┐
│  👤 User Profile        │
├─────────────────────────┤
│  Name: John Smith       │
│  ID: EMP0001            │
│  Dept: Security         │
│  Role: Administrator    │
│  Email: john@company    │
│  Phone: +1-234-567-8900 │
└─────────────────────────┘
```

### **System Information Widget**

```html
┌─────────────────────────┐
│  🚪 System Info         │
├─────────────────────────┤
│  Location: Main Entry   │
│  Department: Security   │
│  Device S/N: EDOMOS-001 │
│  Model: eDOMOS v2.1     │
│  Status: ● Active       │
└─────────────────────────┘
```

---

## 🆕 **USER ONBOARDING PROCESS**

### **Initial Setup Wizard** (NEW)

When a user logs in for the first time without complete profile:

**Step 1: Welcome Screen**
```
Welcome to eDOMOS!
Let's complete your profile to get started.
```

**Step 2: Personal Information**
```
- Full Name
- Employee ID
- Email
- Phone
```

**Step 3: Department & Role**
```
- Select Department (dropdown)
- Select Role (dropdown)
```

**Step 4: Review & Confirm**
```
Please review your information:
[Display all entered data]

[Confirm] [Go Back]
```

**Implementation:**
```python
@app.route('/onboarding')
@login_required
def onboarding():
    user = current_user
    if user.full_name and user.employee_id:
        return redirect('/dashboard')  # Already onboarded
    return render_template('onboarding.html')
```

---

## 🔧 **API REFERENCE**

### **Company Profile**

**GET /api/company-profile**
```json
{
  "company_name": "ABC Corporation",
  "company_address": "123 Main Street",
  "company_city": "New York",
  "company_state": "NY",
  "company_zip": "10001",
  "company_country": "USA",
  "company_phone": "+1-212-555-0100",
  "company_email": "info@abc.com",
  "company_website": "www.abc.com",
  "company_logo_path": "/static/uploads/logo.png"
}
```

**POST /api/company-profile**
```json
{
  "company_name": "New Company Name",
  "company_address": "456 Oak Avenue",
  ...
}
```

Response:
```json
{
  "success": true,
  "message": "Company profile updated successfully"
}
```

### **Door/System Information**

**GET /api/door-system-info**
```json
{
  "door_location": "Main Entrance",
  "department_name": "Quality Control",
  "device_serial_number": "EDOMOS-001",
  "system_model": "eDOMOS v2.1",
  "installation_date": "2025-01-15",
  "last_maintenance_date": "2025-10-01",
  "notes": "Primary access point",
  "is_active": true
}
```

**POST /api/door-system-info**
```json
{
  "door_location": "Side Entrance",
  "department_name": "Production",
  ...
}
```

### **User Management**

**GET /api/users**
```json
{
  "users": [
    {
      "id": 1,
      "username": "admin",
      "full_name": "John Smith",
      "employee_id": "EMP0001",
      "department": "Security",
      "role": "Administrator",
      "email": "john@company.com",
      "phone": "+1-234-567-8900",
      "is_admin": true,
      "is_active": true,
      "created_at": "2025-01-15 10:00:00",
      "last_login": "2025-10-21 09:30:00"
    }
  ]
}
```

**POST /api/users**
```json
{
  "username": "jdoe",
  "password": "SecurePassword123",
  "full_name": "Jane Doe",
  "employee_id": "EMP0002",
  "department": "Production",
  "role": "Operator",
  "email": "jane@company.com",
  "phone": "+1-234-567-8901",
  "is_admin": false
}
```

**PUT /api/users/:id**
```json
{
  "full_name": "Jane Smith",
  "department": "Quality Control",
  "role": "Supervisor",
  ...
}
```

**DELETE /api/users/:id**
```json
{
  "success": true,
  "message": "User deleted successfully"
}
```

---

## 🎨 **CUSTOMIZATION EXAMPLES**

### **Example 1: Manufacturing Company**

```
Company: Precision Parts Manufacturing Inc.
Address: 456 Industrial Drive, Detroit, MI 48201
Door Location: Assembly Line Entrance - Building C
Department: Production
Device S/N: EDOMOS-PRD-003
```

### **Example 2: Hospital**

```
Company: City General Hospital
Address: 789 Medical Plaza, Boston, MA 02101
Door Location: Pharmacy Storage Room
Department: Pharmaceutical Services
Device S/N: EDOMOS-PHR-012
```

### **Example 3: Research Facility**

```
Company: Advanced Research Institute
Address: 321 Innovation Way, San Francisco, CA 94102
Door Location: Laboratory 5 - Clean Room Entry
Department: Quality Control
Device S/N: EDOMOS-LAB-005
```

---

## ✅ **TESTING CHECKLIST**

### **Database Migration**
- [ ] Migration script runs without errors
- [ ] All new tables created
- [ ] New columns added to user table
- [ ] Default data initialized
- [ ] Existing users updated

### **Company Profile**
- [ ] Form loads with existing data
- [ ] Can update company information
- [ ] Logo upload works
- [ ] Logo preview displays correctly
- [ ] Changes persist after refresh

### **Door/System Info**
- [ ] Form loads with existing data
- [ ] Can update all fields
- [ ] Required fields validated
- [ ] Changes save successfully

### **User Management**
- [ ] User list displays all users
- [ ] Can add new user with full profile
- [ ] Can edit existing users
- [ ] Can toggle admin/active status
- [ ] Can delete users (with confirmation)
- [ ] Employee ID uniqueness enforced

### **Dashboard Integration**
- [ ] Company logo displays
- [ ] Company name shows in header
- [ ] User profile widget shows correct data
- [ ] System info widget displays
- [ ] Door location visible

### **Report Integration**
- [ ] PDF includes company header
- [ ] PDF includes system info
- [ ] PDF footer has user details
- [ ] CSV includes additional columns
- [ ] JSON includes metadata

### **User Onboarding**
- [ ] First-time users see onboarding
- [ ] Can complete profile setup
- [ ] Profile validates required fields
- [ ] Redirects to dashboard after completion
- [ ] Doesn't show for existing users

---

## 🐛 **TROUBLESHOOTING**

### **Migration Issues**

**Problem:** "Column already exists" error
**Solution:** Safe to ignore - column already added

**Problem:** "Table not found" during migration
**Solution:** Ensure you're in the correct database directory

### **Logo Upload Issues**

**Problem:** Logo not displaying
**Solution:** Check file permissions on `/static/uploads/` directory

**Problem:** "File too large" error
**Solution:** Reduce image size to under 2MB

### **User Management Issues**

**Problem:** "Employee ID already exists"
**Solution:** Use unique employee IDs (e.g., EMP0001, EMP0002)

**Problem:** Can't edit admin user
**Solution:** Check you have admin permissions

---

## 📞 **SUPPORT & MAINTENANCE**

### **Backup Recommendations**

```bash
# Backup database before migration
cp instance/edomos.db instance/edomos.db.backup_$(date +%Y%m%d)

# Backup after successful migration
cp instance/edomos.db instance/edomos.db.post_migration
```

### **Regular Maintenance**

1. **Weekly:** Review user profiles for accuracy
2. **Monthly:** Update system maintenance date
3. **Quarterly:** Review and update company information
4. **Annually:** Archive old user accounts

---

## 🎉 **CONCLUSION**

The complete customization system provides:
- ✅ Professional branding (logo, company info)
- ✅ Detailed system tracking (door, device, department)
- ✅ Comprehensive user profiles
- ✅ Enhanced reporting with all metadata
- ✅ Better audit compliance
- ✅ Professional appearance

All information flows through:
- Dashboard displays
- PDF/CSV/JSON reports
- User onboarding process
- Access control decisions

---

*Last Updated: October 21, 2025*
*eDOMOS v2.1 - Door Monitoring System*
*Complete Customization & Profile Management System*
