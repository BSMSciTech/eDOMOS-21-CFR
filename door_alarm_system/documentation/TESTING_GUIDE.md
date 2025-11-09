# Electronic Signature Testing Guide

## ✅ Your Server is Running!
Server detected at: http://192.168.31.227:5000

## 🧪 Testing Steps

### 1. Access the Demo Page
Open in your browser:
```
http://192.168.31.227:5000/electronic-signatures
```

### 2. Browser Testing (7 Steps)

#### Step 1: View the Demo Page
- ✅ Page loads without errors
- ✅ 4 demo cards are visible (Change Control, Training, SOP, Validation)
- ✅ Statistics dashboard shows counts
- ✅ Recent signatures table is visible

#### Step 2: Test "Approve Change Control" 
- Click **"Sign Document"** button on the first card
- Modal should popup with signature form
- Enter your password: `admin` (or your actual password)
- Enter reason: `Approving hardware change for testing`
- Click **"Submit Signature"**
- ✅ Success toast message appears
- ✅ Signature appears in "Recent Signatures" table
- ✅ Statistics update automatically

#### Step 3: Test "Complete Training"
- Click **"Sign Training Completion"** on second card
- Enter password and reason: `Completed safety training successfully`
- Submit signature
- ✅ Signature created successfully
- ✅ Event type shows "training_completed"

#### Step 4: Test "Approve SOP"
- Click **"Sign Approval"** on third card
- Enter password and reason: `SOP reviewed and approved`
- Submit signature
- ✅ Signature logged correctly

#### Step 5: Test "Review Validation"
- Click **"Sign Review"** on fourth card
- Enter password and reason: `Validation test results verified`
- Submit signature
- ✅ All 4 signature types working

#### Step 6: Test Password Validation
- Click any sign button
- Enter WRONG password
- ✅ Error message: "Invalid password"
- ✅ Signature NOT created

#### Step 7: Verify Auto-Refresh
- Wait 30 seconds
- ✅ Statistics refresh automatically
- ✅ Signature table updates

---

## 🔬 API Testing (Advanced)

### Test 1: Create Signature
```bash
# First, login to get session cookie
curl -c cookies.txt -X POST http://192.168.31.227:5000/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin"

# Create signature
curl -b cookies.txt -X POST http://192.168.31.227:5000/api/signature/create \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "document_approval",
    "event_id": "TEST-001",
    "reason": "API Testing - Document Approval",
    "password": "admin"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "signature": {
    "id": 5,
    "event_type": "document_approval",
    "signature_hash": "a1b2c3...",
    "timestamp": "2025-10-29T17:05:30"
  }
}
```

### Test 2: Verify Signature
```bash
curl -b cookies.txt http://192.168.31.227:5000/api/signature/verify/1
```

**Expected Response:**
```json
{
  "signature": {
    "id": 1,
    "user": "admin",
    "event_type": "change_control_approval",
    "timestamp": "2025-10-29 16:30:15",
    "ip_address": "192.168.31.227",
    "is_valid": true
  }
}
```

### Test 3: Get User Signatures
```bash
curl -b cookies.txt http://192.168.31.227:5000/api/signature/user/1
```

### Test 4: Get Event Signatures
```bash
curl -b cookies.txt http://192.168.31.227:5000/api/signature/by-event/CHG-2025-001
```

---

## 📊 Database Verification

### Check Signature Count
```bash
python3 -c "
from app import app, db, ElectronicSignature
with app.app_context():
    count = ElectronicSignature.query.count()
    print(f'Total signatures: {count}')
    
    latest = ElectronicSignature.query.order_by(ElectronicSignature.id.desc()).first()
    if latest:
        print(f'Latest: {latest.event_type} by User #{latest.user_id} at {latest.timestamp}')
"
```

### View All Tables
```bash
python3 -c "
from app import app, db
with app.app_context():
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print('Part 11 Tables:', [t for t in tables if any(x in t for x in ['signature', 'training', 'change', 'sop', 'validation'])])
"
```

---

## ✨ What to Look For

### Security Features
- ✅ Password verification required
- ✅ SHA-256 hash generated for each signature
- ✅ IP address captured
- ✅ Blockchain logging (check blockchain stats page)

### User Experience
- ✅ Modal opens smoothly
- ✅ Form validation works (required fields)
- ✅ Success/error toasts display
- ✅ Character counter shows (0/500)
- ✅ Password toggle works (eye icon)
- ✅ Auto-refresh every 30 seconds

### Compliance
- ✅ Timestamps in ISO format
- ✅ Full audit trail (who, what, when, why, where)
- ✅ Digital signature hash unique
- ✅ Cannot modify after creation

---

## 🐛 Troubleshooting

### Problem: Modal doesn't open
**Solution:** Check browser console (F12) for JavaScript errors

### Problem: "Invalid password" error
**Solution:** 
- Verify you're logged in as correct user
- Check your actual password (default: `admin`)
- Try logout/login again

### Problem: Signature not appearing in table
**Solution:** 
- Refresh page manually
- Check browser console for API errors
- Verify server logs for errors

### Problem: API returns 401 Unauthorized
**Solution:**
- You need to login first
- Use cookies.txt to maintain session
- Verify session is active

### Problem: Database error
**Solution:**
```bash
# Re-run migration
python3 run_part11_migration.py
```

---

## 📈 Success Metrics

After testing, you should have:
- ✅ At least 4 signatures created (one of each type)
- ✅ All signatures visible in database
- ✅ Blockchain contains signature events
- ✅ No JavaScript errors in browser console
- ✅ All API endpoints responding correctly

---

## 🎯 Next Steps After Testing

If all tests pass:
1. ✅ Mark Phase 2 as 100% complete
2. 🚀 Proceed to Phase 3: Training Management
3. 📝 Integration with real door events
4. 🔐 Add signature requirements to critical operations

If tests fail:
1. Note which tests failed
2. Check browser console for errors
3. Review server logs
4. Report specific issues for fixing

---

## 💡 Quick URLs

- Demo Page: http://192.168.31.227:5000/electronic-signatures
- Dashboard: http://192.168.31.227:5000/dashboard
- Blockchain Stats: http://192.168.31.227:5000/blockchain-demo
- Compliance Report: http://192.168.31.227:5000/compliance-report

---

**Created:** 2025-10-29  
**Phase:** 2 - Electronic Signatures (Testing)  
**Status:** Ready for execution
