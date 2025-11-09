# 🚀 QUICK START: Remove Red Strikethrough

## ⚡ 3-Step Process

### Step 1: Export Certificate (On Raspberry Pi)
```bash
cd ~/WebApp/eDOMOS-v2.1/door_alarm_system
./export_root_ca.sh
```
This will:
- Copy Root CA to `~/mkcert_export/rootCA.pem`
- Show certificate details
- Offer to start web server for easy download

### Step 2: Download Certificate (On Your Device)

**Option A: Web Download (Easiest)**
- Raspberry Pi: Run `cd ~/mkcert_export && python3 -m http.server 8080`
- Your device: Go to `http://192.168.31.227:8080`
- Download `rootCA.pem`

**Option B: SCP (From your computer)**
```bash
scp bsm@192.168.31.227:~/mkcert_export/rootCA.pem ~/Desktop/
```

### Step 3: Install Certificate

#### Windows (Chrome/Edge)
1. Double-click `rootCA.pem`
2. Install → Local Machine → Trusted Root CA
3. Restart browser

#### macOS (Safari/Chrome)  
1. Double-click `rootCA.pem`
2. Add to Keychain → Trust → Always Trust
3. Restart browser

#### Linux (Ubuntu/Debian)
```bash
sudo cp rootCA.pem /usr/local/share/ca-certificates/mkcert-root.crt
sudo update-ca-certificates
```

#### Android
Settings → Security → Install CA certificate → Select file

#### iOS
Email to yourself → Install Profile → Settings → Certificate Trust Settings → Enable

#### Firefox (All OS)
Settings → Privacy → Certificates → Authorities → Import

---

## ✅ Verification

1. Clear browser cache
2. Restart browser completely
3. Visit: **https://192.168.31.227:5000**

**Expected Result:**
- 🔒 Green padlock
- ✅ "Connection is secure"
- ❌ NO red strikethrough!

---

## 📚 Need More Details?

See: `INSTALL_ROOT_CA.md` for complete step-by-step guides with screenshots

---

## 🆘 Quick Troubleshooting

**Still seeing warning?**
- Clear ALL browser cache/cookies
- Restart browser (close ALL windows)
- Check certificate is in correct store

**Firefox specific?**
- Firefox uses own cert store
- Must import via Firefox settings

---

## 📊 Status

Your Root CA Location: `/home/bsm/.local/share/mkcert/rootCA.pem`

**One-Time Setup:**
- Install certificate on each device ONCE
- All future mkcert certificates will be trusted
- Works for any project using mkcert
