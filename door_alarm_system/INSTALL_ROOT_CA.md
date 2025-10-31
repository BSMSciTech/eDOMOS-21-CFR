# 🔒 How to Remove HTTPS Red Strikethrough (Install mkcert Root CA)

## 📋 Overview

The red strikethrough on "https" in your browser indicates that your self-signed SSL certificate is not trusted. To remove this warning, you need to install the mkcert Root CA (Certificate Authority) on each device that will access your eDOMOS system.

**Current Status:**
- ✅ HTTPS Server: https://192.168.31.227:5000 - **WORKING**
- ✅ Encryption: **ACTIVE** (your connection is already secure)
- ⚠️ Browser Warning: Red strikethrough due to self-signed certificate
- 🎯 Goal: Install Root CA to remove browser warnings

---

## 🔍 Step 1: Locate the mkcert Root CA Certificate

First, find where mkcert stored your root certificate on the Raspberry Pi:

```bash
# Run this command on your Raspberry Pi
mkcert -CAROOT
```

This will show you the directory path (typically `/home/bsm/.local/share/mkcert`)

```bash
# List the certificates in that directory
ls -la $(mkcert -CAROOT)
```

You should see two files:
- `rootCA.pem` - This is the certificate you need to install
- `rootCA-key.pem` - The private key (KEEP THIS SECRET!)

---

## 📤 Step 2: Copy Root CA to Your Devices

### Method 1: Using SCP (from your computer)

**On your Windows/Mac/Linux computer:**

```bash
# Copy rootCA.pem to your computer
scp bsm@192.168.31.227:~/.local/share/mkcert/rootCA.pem ~/Desktop/
```

### Method 2: Using Web Server (temporary)

**On your Raspberry Pi:**

```bash
# Navigate to the certificate directory
cd $(mkcert -CAROOT)

# Start a temporary web server
python3 -m http.server 8080
```

**On your device browser:**
- Go to: `http://192.168.31.227:8080`
- Download `rootCA.pem`
- **Stop the server** (Ctrl+C) after downloading

### Method 3: USB Drive

Copy the `rootCA.pem` file to a USB drive and transfer it to each device.

---

## 💻 Step 3A: Install Root CA on Windows

### Using Chrome/Edge (Chromium-based browsers):

1. **Double-click `rootCA.pem`** (or right-click → Install Certificate)

2. **Certificate Import Wizard** will open:
   - Store Location: Select **"Local Machine"** (requires admin) or **"Current User"**
   - Click **Next**

3. **Certificate Store**:
   - Select **"Place all certificates in the following store"**
   - Click **Browse**
   - Select **"Trusted Root Certification Authorities"**
   - Click **OK** → **Next**

4. **Finish** the wizard
   - Click **Finish**
   - Confirm the security warning: **Yes**

5. **Restart your browser**

### Using Firefox:

1. Open Firefox
2. Go to **Settings** (☰ menu → Settings)
3. Search for **"certificates"**
4. Click **"View Certificates"**
5. Go to **"Authorities"** tab
6. Click **"Import..."**
7. Select `rootCA.pem`
8. Check **"Trust this CA to identify websites"**
9. Click **OK**
10. Restart Firefox

---

## 🍎 Step 3B: Install Root CA on macOS

### For Safari/Chrome (System Keychain):

1. **Double-click `rootCA.pem`** 
   - Keychain Access will open

2. **Add to Keychain**:
   - Select **"login"** or **"System"** keychain
   - Click **"Add"**

3. **Trust the Certificate**:
   - Find "mkcert" certificate in the keychain
   - Double-click it
   - Expand **"Trust"** section
   - Set **"When using this certificate"** to **"Always Trust"**
   - Close window (enter password to save)

4. **Restart your browser**

### For Firefox (same as Windows):

1. Firefox → **Preferences** → **Privacy & Security**
2. **Certificates** → **View Certificates**
3. **Authorities** tab → **Import**
4. Select `rootCA.pem`
5. Check **"Trust this CA to identify websites"**
6. Restart Firefox

---

## 🐧 Step 3C: Install Root CA on Linux

### Ubuntu/Debian (System-wide):

```bash
# Copy certificate to system trust store
sudo cp rootCA.pem /usr/local/share/ca-certificates/mkcert-root.crt

# Update certificate store
sudo update-ca-certificates

# Restart browser
```

### Fedora/RedHat/CentOS:

```bash
# Copy certificate
sudo cp rootCA.pem /etc/pki/ca-trust/source/anchors/mkcert-root.crt

# Update trust store
sudo update-ca-trust

# Restart browser
```

### Firefox on Linux (same as other platforms):

```bash
# Or use Firefox GUI (same as Windows/Mac steps)
```

---

## 📱 Step 3D: Install Root CA on Android

### Method 1: Email Yourself

1. Email `rootCA.pem` to yourself
2. Open email on Android device
3. Download the attachment
4. Go to **Settings** → **Security** → **Encryption & Credentials**
5. Tap **"Install a certificate"** → **"CA certificate"**
6. Select **"Install anyway"** (confirm warning)
7. Browse to downloaded file and select it
8. Enter device PIN/password
9. Certificate installed!

### Method 2: USB Transfer

1. Connect Android to computer via USB
2. Copy `rootCA.pem` to device (Downloads folder)
3. Follow steps 4-9 above

### Method 3: HTTP Download (Temporary Server)

1. On Raspberry Pi: `python3 -m http.server 8080` (in mkcert directory)
2. On Android browser: Go to `http://192.168.31.227:8080`
3. Download `rootCA.pem`
4. Follow installation steps 4-9 above

**Note:** Android will show a persistent notification about installed CA.

---

## 📱 Step 3E: Install Root CA on iOS/iPhone/iPad

### Using AirDrop (Mac to iPhone):

1. On Mac: Right-click `rootCA.pem` → Share → AirDrop
2. Select your iPhone
3. On iPhone: Profile downloaded notification appears

### Using Email/iCloud:

1. Email `rootCA.pem` to yourself
2. Open email on iOS device
3. Tap the attachment

### Installation Steps (both methods):

1. **Install Profile**:
   - Go to **Settings** → **Profile Downloaded** (or **General** → **VPN & Device Management**)
   - Tap the "mkcert" profile
   - Tap **"Install"** (top right)
   - Enter passcode
   - Tap **"Install"** again
   - Tap **"Done"**

2. **Trust the Certificate**:
   - Go to **Settings** → **General** → **About** → **Certificate Trust Settings**
   - Find "mkcert" under **"ENABLE FULL TRUST FOR ROOT CERTIFICATES"**
   - Toggle it **ON** (green)
   - Confirm: **"Continue"**

3. **Restart Safari** (close all tabs, force quit app)

---

## ✅ Step 4: Verify Installation

### Test the Connection:

1. **Clear browser cache** (Ctrl+Shift+Delete or Cmd+Shift+Delete)
2. **Restart your browser completely**
3. Go to: **https://192.168.31.227:5000**

### What You Should See:

**Before Installation:**
- 🔴 Red strikethrough on "https"
- ⚠️ "Not Secure" warning
- Yellow/red padlock icon

**After Installation:**
- ✅ Green padlock icon (locked)
- ✅ "Connection is secure"
- ✅ No red strikethrough
- ✅ Certificate shows: "BSM SciTech"

### Check Certificate Details:

**In Browser:**
1. Click the padlock icon in address bar
2. Click **"Certificate"** or **"Connection is secure"**
3. You should see:
   - **Issued to:** 192.168.31.227
   - **Issued by:** mkcert (Your Name)
   - **Valid until:** October 20, 2035
   - ✅ **Certificate is valid**

---

## 🔧 Troubleshooting

### Issue 1: Certificate Still Not Trusted

**Solution:**
```bash
# Regenerate certificates with explicit trust
cd ~/WebApp/eDOMOS-v2.1/door_alarm_system

# Remove old certificates
rm -rf ssl/

# Reinstall mkcert root CA
mkcert -install

# Regenerate certificates
mkdir -p ssl
cd ssl
mkcert -cert-file cert.pem -key-file key.pem 192.168.31.227 localhost 127.0.0.1 ::1

# Restart server
cd ..
./stop.sh
USE_SSL=true ./start_https.sh
```

### Issue 2: Browser Cache Issues

**Solution:**
1. Clear all browsing data (cache, cookies, history)
2. Close ALL browser windows completely
3. Restart browser
4. Try accessing site again

### Issue 3: Firefox Still Shows Warning

**Solution:**
- Firefox uses its own certificate store (not system)
- Must import through Firefox settings (see Firefox steps above)
- Restart Firefox after importing

### Issue 4: Android "Network May Be Monitored"

**This is NORMAL:**
- Android shows persistent notification when user CA is installed
- It's a security feature, not a problem
- Your network is NOT being monitored
- You installed the CA yourself

### Issue 5: iOS Profile Won't Install

**Solution:**
- Ensure profile is downloaded (check Downloads)
- Profile must have `.pem` or `.crt` extension
- Go to Settings → General → VPN & Device Management
- Don't forget Step 2: Enable trust in Certificate Trust Settings

---

## 🎯 Quick Summary

### For Each Device Type:

| Device | Installation Method | Restart Required |
|--------|-------------------|------------------|
| **Windows** | Double-click → Trusted Root CA | Browser restart |
| **macOS** | Double-click → Keychain → Trust | Browser restart |
| **Linux** | Copy to CA trust store | Browser restart |
| **Android** | Settings → Install CA certificate | No restart |
| **iOS** | Settings → Install Profile → Trust | Safari force-quit |
| **Firefox** | Firefox Settings → Certificates | Firefox restart |

### What Gets Fixed:
- ✅ Red strikethrough removed
- ✅ Green padlock appears
- ✅ "Connection is secure" message
- ✅ No more browser warnings
- ✅ Professional appearance

---

## 🔐 Security Notes

### Important:

1. **Keep `rootCA-key.pem` PRIVATE**
   - Never share this file
   - It's the private key for your CA
   - Anyone with this can create fake certificates

2. **Only `rootCA.pem` Should Be Distributed**
   - This is the public certificate
   - Safe to install on all your devices
   - Only trusts certificates YOU create

3. **Remove CA When No Longer Needed**
   - If you stop using mkcert
   - Uninstall from device certificate stores

4. **This is for Local Network Only**
   - Perfect for home/office use
   - Not for public websites
   - Use Let's Encrypt for public sites

---

## 📞 Need Help?

### Check Installation:

```bash
# On Raspberry Pi - verify mkcert is installed
mkcert -version

# Check if root CA exists
ls -la $(mkcert -CAROOT)

# Verify certificate details
openssl x509 -in ssl/cert.pem -text -noout | grep -A 2 "Subject:"
```

### Test Server:

```bash
# Test HTTPS is working
curl -k https://192.168.31.227:5000/api/test/ping

# Check if port is listening
ss -tlnp | grep 5000
```

### Restart HTTPS Server:

```bash
cd ~/WebApp/eDOMOS-v2.1/door_alarm_system
./stop.sh
USE_SSL=true ./start_https.sh
```

---

## ✨ Expected Result

After installing the Root CA on all your devices:

```
🌐 https://192.168.31.227:5000
   ↑
   ✅ Green padlock, no warnings, professional appearance!
```

**Before:** 🔴 ~~https~~://192.168.31.227:5000 ⚠️ Not Secure

**After:** 🔒 https://192.168.31.227:5000 ✅ Connection is secure

---

## 📝 Summary Checklist

- [ ] Find mkcert root CA location: `mkcert -CAROOT`
- [ ] Copy `rootCA.pem` to your device
- [ ] Install certificate (method depends on OS)
- [ ] Restart browser completely
- [ ] Test: Visit https://192.168.31.227:5000
- [ ] Verify: Green padlock, no warnings
- [ ] Repeat for each device that will access the system

**Status:** All devices with installed Root CA will show secure connection! ✅
