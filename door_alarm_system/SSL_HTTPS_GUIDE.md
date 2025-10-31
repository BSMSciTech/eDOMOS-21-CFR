# eDOMOS v2.1 - SSL/HTTPS Configuration Guide

## ✅ Current Status

**HTTP Server**: Running successfully at http://192.168.31.227:5000
**SSL Certificates**: mkcert certificates installed in `ssl/` directory

## 🚀 Quick Start Commands

### Start HTTP Server (Currently Running):
```bash
./start_http.sh
```
Access at: **http://192.168.31.227:5000**

### Start HTTPS Server:
```bash
./start_https.sh
```
Access at: **https://192.168.31.227:5000**

### Stop Server:
```bash
./stop.sh
```

## 🔒 HTTPS with mkcert Certificates

Your system has **mkcert-generated SSL certificates** that are valid until **2035**.

### Certificate Details:
- **Location**: `ssl/cert.pem` and `ssl/key.pem`
- **Issued for**: 192.168.31.227
- **Issuer**: BSM SciTech / eDOMOS
- **Valid Until**: October 20, 2035

### Why mkcert?
mkcert creates locally-trusted SSL certificates. When you install mkcert's root CA on a device, that device will trust your certificates **without any browser warnings**.

## 🌐 Browser Access Guide

### From the Raspberry Pi (localhost):
- If mkcert was installed on this Pi: **No warnings** ✅
- Open: https://192.168.31.227:5000
- Browser should trust the certificate automatically

### From Another Device (phone, laptop, etc.):

#### Option 1: Install mkcert's Root CA (Recommended - No Warnings)
1. On the Raspberry Pi, get the root CA location:
   ```bash
   mkcert -CAROOT
   ```

2. Copy `rootCA.pem` from that location to your device

3. Install it:
   - **Windows**: Double-click → Install Certificate → Trusted Root Certification Authorities
   - **Mac**: Double-click → Keychain Access → Always Trust
   - **Android**: Settings → Security → Install from storage
   - **iOS**: Email it → Install Profile → Trust

4. Now https://192.168.31.227:5000 will work **without warnings** ✅

#### Option 2: Accept the Warning (Quick but Less Secure)
1. Open https://192.168.31.227:5000
2. You'll see "Your connection is not private" or similar
3. Click "Advanced" → "Proceed to 192.168.31.227 (unsafe)"
4. The page will load (warning will reappear on each visit)

## 🔧 Troubleshooting

### HTTPS won't load / Connection timeout:

**Check 1**: Is the server actually running?
```bash
curl -k https://localhost:5000/api/test/ping
```
Should return: `{"ping":"pong",...}`

**Check 2**: Check firewall (if you have one):
```bash
sudo ufw status
sudo ufw allow 5000/tcp
```

**Check 3**: Restart the server:
```bash
./stop.sh
./start_https.sh
```

**Check 4**: View logs:
```bash
tail -f /tmp/edomos_https.log
```

### HTTP vs HTTPS - Which to use?

#### Use HTTP when:
- ✅ Quick local testing
- ✅ Don't want to deal with certificate warnings
- ✅ Only accessing from the same device
- ✅ Network is already secure (home network)

#### Use HTTPS when:
- ✅ Accessing from multiple devices
- ✅ Want encrypted communication
- ✅ Have installed mkcert root CA on all devices
- ✅ Production/security-focused deployment

## 📝 Manual Start Commands

If scripts don't work, use manual commands:

### HTTP:
```bash
cd /home/bsm/WebApp/eDOMOS-v2.1/door_alarm_system
python app.py
```

### HTTPS:
```bash
cd /home/bsm/WebApp/eDOMOS-v2.1/door_alarm_system
USE_SSL=true python app.py
```

### Background (keeps running after closing terminal):
```bash
cd /home/bsm/WebApp/eDOMOS-v2.1/door_alarm_system
nohup python app.py > /tmp/edomos.log 2>&1 &
```

## 🎯 Current Recommendation

**For now, use HTTP** (already running):
- Access at: http://192.168.31.227:5000
- No certificate warnings
- Works immediately on all devices
- Secure enough for local network

**Later, switch to HTTPS when:**
- You install mkcert root CA on other devices
- You want encrypted communication
- You're accessing from outside your local network

## 📊 Server Status Check

```bash
# Check if server is running
ps aux | grep "python app.py" | grep -v grep

# Test connection
curl http://192.168.31.227:5000/api/test/ping

# View logs
tail -f /tmp/edomos_http.log
```

## 🆘 Need Help?

1. **Server won't start**: Check logs at `/tmp/edomos_http.log` or `/tmp/edomos_https.log`
2. **Can't connect**: Make sure firewall allows port 5000
3. **Certificate errors**: Use HTTP instead, or install mkcert root CA
4. **GPIO errors**: Run with `sudo` if needed

---

**Your HTTP server is currently running at: http://192.168.31.227:5000**  
Open that URL in your browser now! 🚀
