# 🚀 QUICK START - Multi-Level Approval Testing

## ✅ System Ready!

Your 5-level approval system is **LIVE** and ready for testing!

**Access URL**: http://192.168.31.227:5000

---

## 🧪 Quick Test Workflow

### Step 1: Create Change Request as User
```
Login: user1 / user123
Navigate: Change Control → Create Change Request
Action: Fill form and submit
Result: Status = "Pending Supervisor"
```

### Step 2: Supervisor Approval
```
Logout and login: supervisor1 / super123
Navigate: Change Control → View pending request
Action: Click "Supervisor Approval" → Enter password & reason
Result: Status = "Pending Manager"
```

### Step 3: Manager Approval
```
Logout and login: manager1 / manager123
Navigate: Change Control → View request
Action: Click "Manager Approval" → Enter password & reason
Result: Status = "Pending Director"
```

### Step 4: Director Approval
```
Logout and login: director1 / director123
Navigate: Change Control → View request
Action: Click "Director Approval" → Enter password & reason
Result: Status = "Pending Admin"
```

### Step 5: Admin Approval
```
Logout and login: admin / admin123
Navigate: Change Control → View request
Action: Click "Admin Approval" → Enter password & reason
Result: Status = "Approved"
```

### Step 6: Implementation
```
As admin (already logged in)
Action: Click "Mark as Implemented" → Enter password & notes
Result: Status = "Implemented"
```

---

## 👥 All Test Users

| Username    | Password    | Level      |
|-------------|-------------|------------|
| user1       | user123     | user       |
| supervisor1 | super123    | supervisor |
| manager1    | manager123  | manager    |
| director1   | director123 | director   |
| admin       | admin123    | admin      |

---

## 🎯 What to Verify

✅ Each user sees only their approval button  
✅ Timeline shows all 5 approval steps  
✅ Electronic signature created at each step  
✅ Status changes correctly  
✅ Cannot skip approval levels  
✅ Blockchain logs each event  
✅ Final count: 6 electronic signatures  

---

## 📊 Expected Timeline

After full workflow:
1. ✅ Change Requested (user1)
2. ✅ Supervisor Approval (supervisor1) + E-Signature
3. ✅ Manager Approval (manager1) + E-Signature
4. ✅ Director Approval (director1) + E-Signature
5. ✅ Admin Approval (admin) + E-Signature
6. ✅ Implementation (admin) + E-Signature

**Total: 6 Electronic Signatures (5 approvals + 1 implementation)**

---

## 🔍 Verification Points

### Check Database
```bash
cd /home/bsm/WebApp/eDOMOS-21-CFR/eDOMOS-21-CFR/door_alarm_system
./venv/bin/python -c "
import sqlite3
conn = sqlite3.connect('instance/alarm_system.db')
cursor = conn.cursor()

# Check change request status
cursor.execute('SELECT change_number, status FROM change_control')
print('Change Requests:', cursor.fetchall())

# Check electronic signatures
cursor.execute('SELECT COUNT(*) FROM electronic_signature')
print('Total Signatures:', cursor.fetchone()[0])
"
```

### Check Blockchain
```bash
./venv/bin/python -c "
import sqlite3
conn = sqlite3.connect('instance/alarm_system.db')
cursor = conn.cursor()
cursor.execute('SELECT event_type FROM blockchain_event_log ORDER BY timestamp DESC LIMIT 10')
print('Recent Events:', [r[0] for r in cursor.fetchall()])
"
```

---

## 🎉 Success Criteria

✅ All 5 users can login  
✅ User1 can create change request  
✅ Each approver sees correct button  
✅ Statuses progress correctly  
✅ All signatures recorded  
✅ Timeline shows complete history  
✅ No errors in app.log  

---

## 🚨 Troubleshooting

**Problem**: User doesn't see approval button  
**Solution**: Check user's `approval_level` matches required level

**Problem**: Status not changing  
**Solution**: Check password is correct, view app.log for errors

**Problem**: Electronic signature not showing  
**Solution**: Verify signature_reason was entered

---

**Ready to test!** Login at: http://192.168.31.227:5000
