# 🚪 DOOR & SYSTEM INFORMATION SETUP GUIDE

## ✅ **ALREADY IMPLEMENTED!**

The Door & System Information feature is already built into your application! Here's how to use it:

---

## 📍 **HOW TO ACCESS**

### **Step 1: Login as Admin**
1. Go to: `http://192.168.31.22:5000/login`
2. Username: `admin`
3. Password: `admin`

### **Step 2: Navigate to Company Profile**
1. After login, go to: `http://192.168.31.22:5000/company-profile`
2. Scroll down to the **"Door & System Information"** section

---

## 📋 **AVAILABLE FIELDS**

### **1. Door Location** 🚪
- **Field**: Door Location
- **Example**: "Main Entrance", "Building A - Level 2", "Factory Gate 1"
- **Required**: Yes
- **Purpose**: Identifies the physical location of the monitored door

### **2. Department Name** 🏢
- **Field**: Department Name
- **Example**: "Security", "Quality Control", "Production", "Stores"
- **Required**: Yes
- **Purpose**: Which department is responsible for this door

### **3. Device Serial Number** 🔢
- **Field**: Device Serial Number
- **Example**: "EDOMOS-001", "EDOMOS-2024-001", "BSM-SN-12345"
- **Required**: Yes
- **Purpose**: Unique identifier for the monitoring device
- **Note**: Must be unique across all systems

### **4. System Model** 🖥️
- **Field**: System Model
- **Default**: "eDOMOS v2.1"
- **Example**: "eDOMOS v2.1 Enterprise", "eDOMOS v2.1 Standard"
- **Purpose**: Model/version of the monitoring system

### **5. Installation Date** 📅
- **Field**: Installation Date
- **Format**: Date picker (YYYY-MM-DD)
- **Optional**: Yes
- **Purpose**: When the system was installed

### **6. Last Maintenance Date** 🔧
- **Field**: Last Maintenance Date
- **Format**: Date picker (YYYY-MM-DD)
- **Optional**: Yes
- **Purpose**: Track maintenance schedule

### **7. Notes** 📝
- **Field**: Notes
- **Type**: Text area (multi-line)
- **Optional**: Yes
- **Purpose**: Additional information about the door/system

---

## 🎯 **QUICK SETUP EXAMPLE**

Here's a complete example configuration:

```
Door Location: Main Entrance - Building A
Department Name: Security
Device Serial Number: EDOMOS-2024-001
System Model: eDOMOS v2.1 Enterprise
Installation Date: 2024-01-15
Last Maintenance Date: 2024-10-01
Notes: Primary access control point for main building. 
       24/7 monitoring required. Contact Security Dept for issues.
```

---

## 💾 **HOW TO SAVE**

1. Fill in all required fields (marked with red asterisk *)
2. Click the **"Save Door/System Information"** button at the bottom
3. You'll see a green success message: "Door & system information saved successfully!"

---

## 📊 **WHERE THIS INFORMATION APPEARS**

Once saved, your door and system information will automatically appear in:

### **1. PDF Reports** 📄
- **Title Page**: Door location shown in subtitle
- **Report Information Section**: 
  - Door Location: "Main Entrance - Building A"
  - Facility: "Your Company - Department Name"
  - Device S/N: "EDOMOS-2024-001"
- **Footer**: Door location on every page

### **2. CSV Exports** 📊
- Metadata header includes:
  ```
  # Door Location: Main Entrance - Building A
  # Device S/N: EDOMOS-2024-001
  ```
- Additional "Location" column in data rows

### **3. JSON Exports** 📦
- Nested metadata structure:
  ```json
  {
    "metadata": {
      "system": {
        "door_location": "Main Entrance - Building A",
        "department": "Security",
        "device_serial_number": "EDOMOS-2024-001",
        "system_model": "eDOMOS v2.1"
      }
    }
  }
  ```

### **4. Dashboard** 📱
- System info widget (if you add it)
- Real-time status displays

---

## 🔌 **API ACCESS**

You can also configure this via API:

### **Get Current Configuration**
```bash
curl -X GET http://192.168.31.22:5000/api/door-system-info \
  -H "Cookie: session=<your-session-cookie>"
```

### **Update Configuration**
```bash
curl -X POST http://192.168.31.22:5000/api/door-system-info \
  -H "Content-Type: application/json" \
  -H "Cookie: session=<your-session-cookie>" \
  -d '{
    "door_location": "Main Entrance - Building A",
    "department_name": "Security",
    "device_serial_number": "EDOMOS-2024-001",
    "system_model": "eDOMOS v2.1 Enterprise",
    "installation_date": "2024-01-15",
    "last_maintenance_date": "2024-10-01",
    "notes": "Primary access control point"
  }'
```

---

## 📸 **SCREENSHOT GUIDE**

When you access `/company-profile`, you'll see:

```
╔══════════════════════════════════════════════════════╗
║  🚪 Door & System Information                        ║
╠══════════════════════════════════════════════════════╣
║                                                      ║
║  Door Location *                                     ║
║  [Main Entrance - Building A             ]          ║
║                                                      ║
║  Department Name *                                   ║
║  [Security                               ]          ║
║                                                      ║
║  Device Serial Number *                              ║
║  [EDOMOS-2024-001                        ]          ║
║                                                      ║
║  System Model                                        ║
║  [eDOMOS v2.1 Enterprise                 ]          ║
║                                                      ║
║  Installation Date                                   ║
║  [2024-01-15                             ] 📅       ║
║                                                      ║
║  Last Maintenance Date                               ║
║  [2024-10-01                             ] 📅       ║
║                                                      ║
║  Notes                                               ║
║  [Primary access control point for main  ]          ║
║  [building. 24/7 monitoring required.    ]          ║
║                                                      ║
║  [ Save Door/System Information ]                    ║
║                                                      ║
╚══════════════════════════════════════════════════════╝
```

---

## ✅ **DATABASE STATUS**

The database is already set up with the `door_system_info` table:

```sql
-- Table structure
door_system_info:
  - id (Primary Key)
  - door_location (VARCHAR 200, Required)
  - department_name (VARCHAR 100)
  - device_serial_number (VARCHAR 100, Unique)
  - system_model (VARCHAR 100, Default: "eDOMOS v2.1")
  - installation_date (DATE)
  - last_maintenance_date (DATE)
  - notes (TEXT)
  - is_active (BOOLEAN, Default: True)
  - updated_at (TIMESTAMP)
```

Default values were already created during migration:
- Door Location: "Main Entrance"
- Department: "Security"
- Device Serial Number: "EDOMOS-001"
- System Model: "eDOMOS v2.1"

---

## 🎯 **RECOMMENDED CONFIGURATION**

For a professional setup, configure it like this:

**Door Location**: Use descriptive, hierarchical names
- ✅ Good: "Main Entrance - Building A - Level 1"
- ✅ Good: "Factory Gate 3 - South Wing"
- ❌ Bad: "Door 1"
- ❌ Bad: "The door"

**Department Name**: Use official department names
- ✅ Good: "Security & Access Control"
- ✅ Good: "Quality Assurance Department"
- ❌ Bad: "QC"
- ❌ Bad: "security"

**Device Serial Number**: Use a systematic naming scheme
- ✅ Good: "EDOMOS-2024-001" (with year)
- ✅ Good: "BSM-SITE1-GATE-001" (with location code)
- ❌ Bad: "123"
- ❌ Bad: "device1"

---

## 🔧 **TROUBLESHOOTING**

### **Issue: Can't access /company-profile page**
- **Solution**: Make sure you're logged in as admin

### **Issue: "Device Serial Number already exists" error**
- **Solution**: Each device must have a unique serial number. Change it to something unique.

### **Issue: Information not showing in reports**
- **Solution**: Make sure you clicked "Save Door/System Information" button

### **Issue: Changes not persisting**
- **Solution**: Check browser console for errors. Verify API endpoint is working.

---

## 📝 **TESTING CHECKLIST**

1. [ ] Navigate to `/company-profile`
2. [ ] Scroll to "Door & System Information" section
3. [ ] Fill in all required fields (*)
4. [ ] Click "Save Door/System Information"
5. [ ] See success message
6. [ ] Refresh page - verify data persists
7. [ ] Generate a PDF report
8. [ ] Verify door location appears in report
9. [ ] Verify device serial number appears in report

---

## 🎉 **SUMMARY**

**Everything is already built and working!** You just need to:

1. ✅ Login as admin
2. ✅ Go to `/company-profile`
3. ✅ Fill in the Door & System Information section
4. ✅ Click Save
5. ✅ Generate a report to see it in action

**No code changes needed - just configure it!** 🚀

---

**Created**: October 21, 2025  
**Status**: ✅ Fully Functional  
**Location**: `http://192.168.31.22:5000/company-profile`
