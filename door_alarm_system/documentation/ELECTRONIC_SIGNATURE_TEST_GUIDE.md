# Electronic Signature Testing Guide
## Step-by-Step Instructions

### Prerequisites
✅ Flask server running (already running on HTTPS)
✅ Logged in as admin user
✅ Browser open to: https://localhost:5000

---

## STEP 1: Access the Electronic Signatures Page

1. **Navigate to Electronic Signatures**
   - Look at the top navigation bar
   - Find the dropdown menu labeled **"21 CFR Part 11"**
   - Click on it to expand
   - Click **"Electronic Signatures"**
   - URL should change to: `https://localhost:5000/electronic-signatures`

2. **What you should see:**
   - Page title: "Electronic Signatures"
   - Subtitle: "21 CFR Part 11 Compliant Digital Signatures"
   - FDA Part 11 Compliant badge (purple gradient)
   - Blue info box explaining the compliance features
   - Left side: 4 demo action cards
   - Right side: Recent Signatures log and statistics

---

## STEP 2: Test Your First Electronic Signature

### Test Action: Approve Change Control

1. **Click the first demo action card:**
   - Card labeled: **"Approve Change Control"**
   - Green checkmark icon
   - Description: "Sign to approve system change CC-DEMO-001"

2. **Signature Modal Appears:**
   You should see a popup modal with:
   - Title: "Electronic Signature Required"
   - Action field showing: "Approve Change Control Request CC-DEMO-001"
   - Username field (pre-filled with your username)
   - Password field (empty - you must enter your password)
   - Reason/Meaning field (empty - you must provide a reason)

3. **Fill out the signature form:**
   - **Username:** (already filled - don't change)
   - **Password:** Enter your account password
   - **Reason/Meaning:** Type something like:
     ```
     Reviewed the change request. All documentation is complete. 
     Change has been tested and approved for implementation.
     ```

4. **Click "Sign" button**

5. **What happens:**
   - Modal closes
   - Green success notification appears: "✓ Electronic signature created successfully"
   - The "Recent Signatures" panel on the right refreshes automatically
   - Your new signature appears at the top of the list
   - Statistics update (Total, Today, Your Signatures counters increment)

6. **Verify the signature entry shows:**
   - ✓ Action: "Approve Change Control Request CC-DEMO-001"
   - ✓ Hash: First 16 characters of SHA-256 hash (e.g., "a3f8d92e1b6c4...")
   - ✓ Event Type badge: "change_control" (green)
   - ✓ Reason: Your entered reason text
   - ✓ Timestamp: Current date/time
   - ✓ IP Address: Your IP (127.0.0.1 or ::1 for localhost)

---

## STEP 3: Test Other Signature Types

### Test each of the 4 demo actions:

1. **Complete Training** (Blue icon)
   - Action: "Complete Training Module: 21 CFR Part 11 Basics"
   - Event Type: training
   - Reason example: "I have completed all training materials and passed the assessment with 95% score"

2. **Approve SOP** (Yellow/Orange icon)
   - Action: "Approve Standard Operating Procedure SOP-001"
   - Event Type: sop
   - Reason example: "Reviewed SOP version 2.1. Content is accurate and follows regulatory requirements"

3. **Review Validation** (Purple icon)
   - Action: "Review IQ Validation Test Results VT-2025-001"
   - Event Type: validation
   - Reason example: "Reviewed all IQ test results. All tests passed. System meets specifications"

### For each test:
- Click the demo card
- Enter your password
- Enter a meaningful reason
- Click "Sign"
- Verify it appears in the Recent Signatures log

---

## STEP 4: Verify Signature Data Integrity

### Check the Recent Signatures Panel

1. **Verify each signature shows:**
   - ✓ Unique SHA-256 hash (first 16 chars displayed)
   - ✓ Correct action description
   - ✓ Your entered reason
   - ✓ Accurate timestamp
   - ✓ Your IP address
   - ✓ Correct event type badge

2. **Click the "Refresh" button**
   - All signatures should reload
   - Data should remain unchanged (immutable)

3. **Check statistics:**
   - Total Signatures: Should equal number of signatures created
   - Today: Should show count of signatures created today
   - Your Signatures: Should match your signature count

---

## STEP 5: Verify Database Storage

### Option A: Check via Database Query
```bash
# In a terminal, run:
cd /home/bsm/WebApp/eDOMOS-21-CFR/eDOMOS-21-CFR/door_alarm_system
./venv/bin/python
```

```python
from app import app, db
from models import ElectronicSignature

with app.app_context():
    signatures = ElectronicSignature.query.order_by(ElectronicSignature.timestamp.desc()).limit(5).all()
    for sig in signatures:
        print(f"\nSignature ID: {sig.id}")
        print(f"User: {sig.user.username}")
        print(f"Action: {sig.action}")
        print(f"Event Type: {sig.event_type}")
        print(f"Reason: {sig.reason}")
        print(f"Hash: {sig.signature_hash}")
        print(f"IP: {sig.ip_address}")
        print(f"Timestamp: {sig.timestamp}")
        print("-" * 50)
```

### Option B: Check via Blockchain Verification
1. Navigate to **"Blockchain"** → **"Blockchain Events"** in the menu
2. Look for entries with type "SIGNATURE_CREATED"
3. Each electronic signature should have a corresponding blockchain entry
4. This proves signatures are immutable and tamper-proof

---

## STEP 6: Test Error Handling

### Test Invalid Password
1. Click any demo action card
2. Enter **wrong password**
3. Click "Sign"
4. **Expected result:** Error message "Invalid password" or authentication failure
5. Signature should NOT be created

### Test Empty Reason
1. Click any demo action card
2. Enter correct password
3. Leave **Reason field empty**
4. Click "Sign"
5. **Expected result:** Browser validation error (HTML5 required field)
6. Cannot submit without reason

### Test Cancel
1. Click any demo action card
2. Click "Cancel" or close the modal
3. **Expected result:** Modal closes, no signature created

---

## STEP 7: Verify 21 CFR Part 11 Compliance

### Check that signatures include ALL required elements:

✅ **§11.50 - Signature Manifestations**
- Action being signed is clearly displayed
- User's name is recorded
- Timestamp is recorded

✅ **§11.100 - General Requirements**
- Password verification (re-entry) is required
- User cannot sign without authentication

✅ **§11.200 - Signature Components**
- Signed action is recorded (what was signed)
- Signer's identity is verified (username + password)
- Meaning of signature is documented (reason field)
- Date and time are captured

✅ **§11.300 - Controls for Electronic Signatures**
- Non-repudiation: SHA-256 hash prevents tampering
- Audit trail: IP address and timestamp captured
- Immutability: Stored in blockchain

---

## Expected Results Summary

After completing all tests, you should have:

1. ✅ **4+ signatures created** (one for each demo action)
2. ✅ **All signatures visible** in Recent Signatures panel
3. ✅ **Statistics updated** correctly
4. ✅ **Each signature contains:**
   - SHA-256 hash
   - Action description
   - Your username
   - Your reason/meaning
   - Timestamp
   - IP address
   - Event type classification
5. ✅ **All signatures stored in database** (verified via query)
6. ✅ **All signatures logged in blockchain** (immutable audit trail)
7. ✅ **Error handling works** (invalid password rejected, empty reason blocked)

---

## Troubleshooting

### Problem: Modal doesn't appear when clicking demo cards
**Solution:** 
- Check browser console for JavaScript errors (F12)
- Verify `signature-modal.js` is loaded (check Network tab)
- Refresh the page (Ctrl+F5)

### Problem: "Invalid password" error with correct password
**Solution:**
- Verify you're using the exact password for your account
- Password is case-sensitive
- Try logging out and back in to confirm password

### Problem: Signatures not appearing in the log
**Solution:**
- Click the "Refresh" button
- Check browser console for API errors
- Verify `/api/signature/user/<user_id>` endpoint is working

### Problem: Statistics show "-" instead of numbers
**Solution:**
- Check browser console for API errors
- Verify JavaScript is enabled
- Refresh the page

---

## What to Look For in a Customer Demo

When demonstrating to pharmaceutical customers, emphasize:

1. **Password Re-entry Requirement**
   - "Notice how the system requires me to re-enter my password. This ensures only authorized users can sign, meeting FDA's identity verification requirement."

2. **Meaningful Reason**
   - "The system forces me to document WHY I'm signing. This isn't optional - it's required by 21 CFR Part 11 §11.200."

3. **Cryptographic Hash**
   - "See this hash code? It's a SHA-256 cryptographic signature. If anyone tries to alter this record, the hash will change and we'll know it's been tampered with."

4. **Complete Audit Trail**
   - "Every signature captures: who signed, what they signed, why they signed, when they signed, and from which IP address. This is exactly what FDA auditors look for."

5. **Blockchain Integration**
   - "These signatures are also recorded in our blockchain audit trail, making them completely immutable. Once signed, the record cannot be changed or deleted."

6. **Non-Repudiation**
   - "With the password verification, cryptographic hash, and blockchain storage, signers cannot later deny that they performed this action. This is legally binding."

---

## Next Steps

Once you've successfully tested Electronic Signatures, we'll move to:
- **Training Management** (employee training tracking with expiration)
- **Change Control** (formal approval workflow for system changes)
- **Validation IQ/OQ/PQ** (installation/operational/performance qualification)

Each module integrates with Electronic Signatures for approval workflows!
