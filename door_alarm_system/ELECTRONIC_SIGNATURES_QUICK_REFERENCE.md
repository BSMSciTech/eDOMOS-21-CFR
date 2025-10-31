# Electronic Signatures - Quick Reference Guide

## 🚀 Phase 2 Complete (70%)

### What Just Got Built

**Electronic Signature System** - FDA 21 CFR Part 11 Compliant  
**Files Created:** 3 new, 2 modified (~880 lines of code)  
**Time:** 2 hours  
**Status:** Ready for testing

---

## Quick Links

- **Demo Page:** http://your-server:5000/electronic-signatures
- **API Docs:** See below
- **Navigation:** Blockchain → Electronic Signatures

---

## How to Use (User Perspective)

### Step 1: Access the Demo Page
1. Login to eDOMOS
2. Click "Blockchain" in navigation
3. Click "Electronic Signatures"

### Step 2: Try a Signature
1. Click any demo action card:
   - "Approve Change Control"
   - "Complete Training"
   - "Approve SOP"
   - "Review Validation Test"

2. Modal will open showing:
   - Action description
   - Password field (re-enter your password)
   - Reason field (explain why you're signing)
   - Auto-captured info (user, timestamp, IP)

3. Fill in:
   - Password: your actual password
   - Reason: meaningful explanation (min 10 chars)

4. Click "Sign Electronically"

5. Success! Signature appears in log on right side

---

## API Reference

### 1. Create Signature
```bash
POST /api/signature/create
Content-Type: application/json

{
    "event_id": 123,
    "event_type": "change_control",
    "action": "Approve Change Control CC-2025-001",
    "reason": "Reviewed all documentation and test results",
    "password": "your_password"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Electronic signature created successfully",
    "signature": {
        "id": 456,
        "signature_hash": "a7f3e2d1...",
        "timestamp": "2025-10-29T10:30:00",
        "user": "john_doe",
        "ip_address": "192.168.1.100"
    }
}
```

### 2. Verify Signature
```bash
GET /api/signature/verify/456
```

**Response:**
```json
{
    "success": true,
    "signature": {
        "id": 456,
        "user": "john_doe",
        "action": "Approve Change Control...",
        "reason": "Reviewed all documentation...",
        "signature_hash": "a7f3e2d1...",
        "timestamp": "2025-10-29T10:30:00",
        "ip_address": "192.168.1.100"
    }
}
```

### 3. Get Signatures by Event
```bash
GET /api/signature/by-event/123?event_type=change_control
```

### 4. Get User Signatures
```bash
GET /api/signature/user/1?limit=50&offset=0
```

---

## JavaScript Usage

### Basic Example
```javascript
showSignatureModal({
    action: 'Approve my document',
    event_id: 123,
    event_type: 'document_approval',
    username: 'current_username',
    onSuccess: function(signature) {
        console.log('Signature created:', signature);
        // Do something after signing
    },
    onCancel: function() {
        console.log('User cancelled');
    }
});
```

### Integration Example (Change Control)
```javascript
// On "Approve" button click
document.getElementById('approveBtn').addEventListener('click', function() {
    showSignatureModal({
        action: 'Approve Change Control CC-2025-001',
        event_id: changeControlId,
        event_type: 'change_control',
        username: currentUser,
        onSuccess: function(signature) {
            // Update change control status
            fetch(`/api/change-control/${changeControlId}/approve`, {
                method: 'POST',
                body: JSON.stringify({ signature_id: signature.id })
            }).then(response => {
                alert('Change control approved and signed!');
                location.reload();
            });
        }
    });
});
```

---

## Compliance Features

### What Gets Captured (§11.200)
- ✅ User ID (who signed)
- ✅ Password verification (identity proof)
- ✅ Reason for signing (§11.50)
- ✅ Timestamp (when signed)
- ✅ IP address (where signed)
- ✅ Signature hash (SHA-256)
- ✅ Event details (what was signed)

### Security Features
- ✅ Password verified using bcrypt
- ✅ SHA-256 cryptographic hash
- ✅ Blockchain audit trail
- ✅ Non-repudiation (cannot deny)
- ✅ Immutable record

---

## Testing Checklist

### Browser Testing
- [ ] Navigate to /electronic-signatures
- [ ] Page loads without errors
- [ ] Demo cards are clickable
- [ ] Modal opens when clicking card
- [ ] Password field works
- [ ] Reason field works
- [ ] Character counter updates
- [ ] Password toggle button works
- [ ] Submit button creates signature
- [ ] Success toast appears
- [ ] Signature appears in log
- [ ] Statistics update

### API Testing
```bash
# Test create signature
curl -X POST http://localhost:5000/api/signature/create \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": 123,
    "event_type": "test",
    "action": "Test signature",
    "reason": "Testing the API endpoint",
    "password": "admin"
  }'

# Test verify signature
curl http://localhost:5000/api/signature/verify/1

# Test get by user
curl http://localhost:5000/api/signature/user/1
```

### Database Testing
```sql
-- Check signatures were created
SELECT * FROM electronic_signature ORDER BY timestamp DESC LIMIT 10;

-- Check blockchain entries
SELECT * FROM blockchain_event_log 
WHERE event_type = 'electronic_signature' 
ORDER BY timestamp DESC LIMIT 10;
```

---

## Troubleshooting

### Modal doesn't open
- **Check:** Is signature-modal.js loaded?
- **Fix:** Add `<script src="/static/js/signature-modal.js"></script>` to template

### "Incorrect password" error
- **Check:** Are you entering the correct password?
- **Fix:** Reset password if forgotten

### Signature doesn't appear in log
- **Check:** Browser console for errors
- **Check:** API response status
- **Fix:** Refresh page manually or check network tab

### "Failed to create signature" error
- **Check:** Backend logs for Python errors
- **Check:** Database connection
- **Fix:** Review server logs for details

---

## File Locations

```
door_alarm_system/
├── app.py                              # API endpoints added here
├── models.py                            # ElectronicSignature model
├── static/
│   └── js/
│       └── signature-modal.js          # NEW: Modal component
└── templates/
    ├── base.html                        # Navigation updated
    └── electronic_signatures.html       # NEW: Demo page
```

---

## Next Steps

### Today
1. ✅ Code complete
2. ⏳ Test in browser
3. ⏳ Fix any bugs
4. ⏳ Verify blockchain integration

### This Week
1. Integrate with change control
2. Add to training completion
3. Create signature badge component
4. Add to dashboard

### Next Week (Phase 3)
1. Build training management UI
2. Add training assignment workflow
3. Integrate signatures with training

---

## FAQ

**Q: Can users sign without password?**  
A: No, password is required per §11.200 for identity verification.

**Q: What if user forgets why they signed?**  
A: Reason is permanently stored and can be viewed in signature history.

**Q: Can signatures be deleted?**  
A: No, signatures are immutable once created (Part 11 requirement).

**Q: Can admins sign for other users?**  
A: No, each user must sign personally (non-repudiation).

**Q: How long are signatures valid?**  
A: Signatures don't expire - they're permanent records.

**Q: Can I see who signed what?**  
A: Yes, use the signature log or API endpoints.

**Q: Is this legally binding?**  
A: Yes, electronic signatures are legally equivalent to handwritten signatures per 21 CFR Part 11.

---

## Support

**Documentation:** See `21_CFR_PART11_PHASE2_PROGRESS.md`  
**API Docs:** This file (Quick Reference)  
**Issues:** Check browser console + server logs  
**Questions:** Review PART11_VISUAL_OVERVIEW.md for architecture

---

**Status:** Phase 2 at 70% - Ready for Testing ✅  
**Next Milestone:** 100% Phase 2 (testing complete)  
**ETA:** 1-2 days
