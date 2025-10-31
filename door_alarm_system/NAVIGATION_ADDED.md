# 🎯 NAVIGATION UPDATED - HOW TO ACCESS COMPANY PROFILE

## ✅ **CHANGES MADE**

I've added two new navigation links to the top menu bar (Admin section):

### **NEW MENU ITEMS:**
1. 🏢 **Company Profile** - Configure company & door/system info
2. 👥 **Users** - Manage user accounts and profiles

---

## 📍 **WHERE TO FIND IT**

After you refresh your browser, you'll see the navigation bar like this:

```
╔════════════════════════════════════════════════════════════════╗
║ eDOMOS v2.1  [Dashboard] [Event Log] [Reports] [Analytics]   ║
║              [Company Profile] [Users] [Admin]  👤 admin ▼    ║
╚════════════════════════════════════════════════════════════════╝
```

### **Navigation Structure:**

**For All Users:**
- 📊 Dashboard
- 📝 Event Log  
- 📄 Reports
- 📈 Analytics

**For Admins Only:**
- 🏢 **Company Profile** ← NEW! (Configure door & system info)
- 👥 **Users** ← NEW! (Manage user accounts)
- 🔒 Admin (Settings & system admin)

---

## 🚀 **HOW TO ACCESS**

### **Method 1: Using Navigation Menu** (Easiest)
1. Make sure your application is running
2. Open browser: `http://192.168.31.22:5000`
3. Login as admin
4. Look at the top navigation bar
5. Click on **"Company Profile"** link (with 🏢 building icon)

### **Method 2: Direct URL**
```
http://192.168.31.22:5000/company-profile
```

### **Method 3: Users Management**
```
http://192.168.31.22:5000/user-management
```

---

## 🎨 **WHAT YOU'LL SEE**

### **Company Profile Page:**
When you click "Company Profile", you'll see:

```
╔══════════════════════════════════════════════════════════════╗
║  Company Profile Management                                  ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  📋 Company Information                                      ║
║  ┌──────────────────────────────────────────────────────┐  ║
║  │ Company Name: [                              ]       │  ║
║  │ Address: [                                   ]       │  ║
║  │ City: [          ] State: [    ] ZIP: [     ]       │  ║
║  │ ...                                                  │  ║
║  └──────────────────────────────────────────────────────┘  ║
║                                                              ║
║  🖼️ Company Logo                                            ║
║  ┌──────────────────────────────────────────────────────┐  ║
║  │ [Choose File] Upload logo (PNG/JPG/SVG, max 2MB)    │  ║
║  └──────────────────────────────────────────────────────┘  ║
║                                                              ║
║  🚪 Door & System Information                               ║
║  ┌──────────────────────────────────────────────────────┐  ║
║  │ Door Location: [Main Entrance                ]       │  ║
║  │ Department: [Security                        ]       │  ║
║  │ Device S/N: [EDOMOS-001                      ]       │  ║
║  │ Model: [eDOMOS v2.1                          ]       │  ║
║  └──────────────────────────────────────────────────────┘  ║
║                                                              ║
║  [Save Company Information] [Save Door/System Info]         ║
╚══════════════════════════════════════════════════════════════╝
```

---

## 🔄 **RESTART THE APPLICATION**

Since the navigation template was updated, you need to restart the app:

### **Option 1: Restart in Terminal**
Press `Ctrl+C` to stop the app, then:
```bash
python3 app.py
```

### **Option 2: Just Refresh Browser**
If the app is already running, just refresh the page (F5 or Ctrl+R)

---

## ✅ **QUICK TEST CHECKLIST**

1. [ ] Restart application (Ctrl+C, then `python3 app.py`)
2. [ ] Open browser: `http://192.168.31.22:5000`
3. [ ] Login as admin
4. [ ] Look at top navigation bar
5. [ ] See "Company Profile" link (with building icon 🏢)
6. [ ] See "Users" link (with users icon 👥)
7. [ ] Click "Company Profile"
8. [ ] Scroll down to "Door & System Information"
9. [ ] Fill in your door/system details
10. [ ] Click "Save Door/System Information"
11. [ ] See success message!

---

## 🎯 **FILL IN YOUR DOOR & SYSTEM INFO**

Now that you can access it, configure these fields:

### **Required Fields:**
| Field | What to Enter | Example |
|-------|---------------|---------|
| **Door Location** | Physical location | "Main Entrance - Building A" |
| **Department Name** | Responsible department | "Security" or "Quality Control" |
| **Device Serial Number** | Unique device ID | "EDOMOS-2024-001" |
| **System Model** | Model/version | "eDOMOS v2.1 Enterprise" |

### **Optional Fields:**
- Installation Date
- Last Maintenance Date
- Notes (additional information)

---

## 📊 **AFTER YOU SAVE**

Once you configure and save the door/system information, it will automatically appear in:

✅ **All PDF Reports** - Header, footer, and information section  
✅ **All CSV Exports** - Metadata header with your details  
✅ **All JSON Exports** - Nested metadata structure  

---

## 🐛 **TROUBLESHOOTING**

### **Issue: Still don't see the links**
**Solution:** 
1. Make sure you're logged in as **admin**
2. Refresh the page (F5)
3. Clear browser cache (Ctrl+Shift+R)
4. Restart the application

### **Issue: Links are there but page shows "Permission Denied"**
**Solution:** You must be logged in as admin user

### **Issue: Page shows 404 Not Found**
**Solution:** 
- Check that the route `/company-profile` exists
- Verify you're running the latest version of app.py
- Restart the application

---

## 🎉 **SUMMARY**

**✅ Navigation Updated:**
- Added "Company Profile" link to top menu
- Added "Users" link to top menu
- Both visible only to admin users

**✅ How to Access:**
1. Restart app: `python3 app.py`
2. Open: `http://192.168.31.22:5000`
3. Login as admin
4. Click "Company Profile" in top menu
5. Configure your door & system information!

---

**Updated**: October 21, 2025  
**Status**: ✅ Navigation links added  
**Restart Required**: Yes (Ctrl+C, then `python3 app.py`)

🚀 **Now you can easily access and configure your door & system information!**
