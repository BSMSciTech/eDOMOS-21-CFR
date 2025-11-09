# eDOMOS v2.1 - Quick Start Guide
## System Improvements Applied

---

## 🎯 WHAT'S NEW?

### 1. ✅ Database Tables Created
- **company_profile** table with logo, address, contact info (12 fields)
- **door_system_info** table with location, department, serial number (10 fields)
- Default data already inserted and ready to customize

### 2. ✅ Streamlined Admin Panel
- Removed duplicate user management features
- Focused on essential system settings only:
  * ⏱️ Timer Configuration
  * 📧 Email Notifications
  * 🔗 Quick Access Links
  * 📊 System & Security Status

### 3. ✅ Modern Color System
- Professional blue theme with security colors
- Consistent design across entire application
- Smooth gradients, shadows, and transitions
- Better visual hierarchy

---

## 🚀 HOW TO USE

### Step 1: Restart the Application
```bash
# Press Ctrl+C to stop the current app
cd /home/bsm/WebApp/eDOMOS-v2.1/door_alarm_system
python3 app.py
```

### Step 2: Login
- Navigate to: http://192.168.31.22:5000
- Username: `admin`
- Password: `admin`

### Step 3: Explore New Features

#### New Admin Panel (Streamlined)
```
Click "Admin" in navigation bar → See:
├── Timer Configuration (set alarm delay)
├── Email Settings (Gmail notifications)
├── Quick Access Cards
│   ├── User Management
│   ├── Company Profile
│   └── Event Logs
├── System Information
└── Security Status
```

#### User Management (Separate Page)
```
Click "Users" in navigation bar → Full user management:
├── Create users with profiles
├── Edit employee details
├── Manage permissions
└── Delete users
```

#### Company Profile (Separate Page)
```
Click "Company Profile" in navigation bar → Configure:
├── Company Information (name, address, contact)
├── Logo Upload
└── Door & System Info (location, department, serial number)
```

---

## 🎨 VISUAL IMPROVEMENTS

### Color Theme
- **Primary Blue:** #3b82f6 (buttons, headers, actions)
- **Success Green:** #10b981 (online status, confirmations)
- **Danger Red:** #ef4444 (alerts, errors)
- **Warning Amber:** #f59e0b (warnings, notifications)
- **Neutral Grays:** Professional backgrounds and text

### Design Elements
- ✨ Smooth gradient backgrounds on cards
- ✨ Subtle shadows with hover effects
- ✨ Rounded corners throughout
- ✨ Consistent spacing and typography
- ✨ Modern icon integration

---

## 📋 ADMIN PANEL COMPARISON

### OLD ADMIN PANEL (admin.html)
```
❌ Create User Form (duplicated)
❌ Basic User Table (inferior)
❌ System Settings (mixed in)
❌ Cluttered interface
❌ No clear organization
```

### NEW ADMIN PANEL (admin_streamlined.html)
```
✅ Timer Configuration Section (focused)
✅ Email Settings Section (clear)
✅ Quick Access Links (organized)
✅ System Info Display (informative)
✅ Security Status (at-a-glance)
✅ No duplicate features
✅ Clean, modern design
```

---

## 🔧 CONFIGURATION GUIDE

### Configure Timer
1. Go to Admin Panel
2. Find "Timer Configuration" section
3. Set duration (seconds)
4. Click "Save Timer Settings"

### Configure Email Alerts
1. Go to Admin Panel
2. Find "Email Notification Settings" section
3. Enter Gmail address
4. Generate App Password: https://myaccount.google.com/apppasswords
5. Add recipient emails (comma-separated)
6. Click "Save Email Settings"

### Manage Users
1. Click "Users" in navigation (or "User Management" card in Admin)
2. Click "Add New User" button
3. Fill in profile details:
   - Username, Password
   - Full Name, Employee ID
   - Department, Role
   - Email, Phone
4. Set permissions
5. Click "Save"

### Update Company Profile
1. Click "Company Profile" in navigation (or card in Admin)
2. Update company information
3. Upload logo (PNG/JPG/SVG)
4. Configure door system details:
   - Door Location
   - Department
   - Device Serial Number
   - System Model
5. Click "Save"

---

## 📊 DATABASE STATUS

### Tables Created
```sql
✅ company_profile (12 columns, 1 default record)
   ├── company_name: "eDOMOS Security Systems"
   ├── company_address: "123 Main Street"
   ├── company_city: "Tech City"
   ├── company_state: "CA"
   ├── company_country: "USA"
   ├── company_phone: "+1-555-0100"
   ├── company_email: "admin@edomos.com"
   └── logo_path: NULL (upload a logo!)

✅ door_system_info (10 columns, 1 default record)
   ├── door_location: "Main Entrance"
   ├── department_name: "Security"
   ├── device_serial_number: "EDOMOS-001"
   ├── system_model: "eDOMOS v2.1"
   └── is_active: 1
```

### Verify Tables
```bash
cd /home/bsm/WebApp/eDOMOS-v2.1/door_alarm_system
python3 create_tables.py
```

---

## 🎯 QUICK CHECKLIST

After restarting the app:

- [ ] Login at http://192.168.31.22:5000
- [ ] Notice new color scheme (blue theme)
- [ ] Click "Admin" - see streamlined panel
- [ ] Click "Users" - see full user management
- [ ] Click "Company Profile" - see company/door config
- [ ] Configure timer duration (Admin Panel)
- [ ] Set up email alerts (Admin Panel)
- [ ] Update company information (Company Profile)
- [ ] Configure door system details (Company Profile)
- [ ] Create a test user (User Management)

---

## 💡 KEY BENEFITS

### For Administrators
✅ Clearer navigation - no confusion between Admin and Users pages
✅ Focused admin panel - only system settings
✅ Quick access to all management features
✅ Better visual organization

### For System
✅ Company branding in reports (logo, info)
✅ Door system tracking (location, department, serial)
✅ User profiles for accountability
✅ Professional appearance for audits

### For Users
✅ Modern, consistent interface
✅ Clear visual hierarchy
✅ Smooth interactions
✅ Accessible design

---

## 🆘 TROUBLESHOOTING

### Can't see new admin panel?
→ Make sure you restarted the app (Ctrl+C then python3 app.py)

### Colors not showing?
→ Clear browser cache (Ctrl+Shift+R)

### Database tables missing?
→ Run: `python3 create_tables.py`

### Email not working?
→ Generate Gmail App Password: https://myaccount.google.com/apppasswords

---

## 📁 FILES TO KNOW

### New Files Created
- `static/css/colors.css` - Modern color system
- `templates/admin_streamlined.html` - New admin interface
- `create_tables.py` - Database setup script

### Files Modified
- `app.py` - Updated imports and admin route
- `templates/base.html` - Added color system stylesheet

### Old Files (Backup)
- `templates/admin.html` - Old admin panel (kept as backup)
- `templates/admin_backup.html` - Previous backup

---

## ✅ SUMMARY

**All 3 tasks completed:**
1. ✅ Database tables created with default data
2. ✅ Admin panel streamlined (no duplicates)
3. ✅ Modern color system implemented

**Next steps:**
1. Restart app
2. Login and explore
3. Configure settings
4. Customize company profile

**You're ready to go!** 🚀
