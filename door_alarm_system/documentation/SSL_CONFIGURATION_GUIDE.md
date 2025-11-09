# 🔐 SSL/HTTPS Configuration Guide for eDOMOS v2.1

## 📋 Overview

Your eDOMOS system now supports **HTTPS encryption** using SSL/TLS certificates. The SSL certificate has been automatically generated and integrated into your Flask application.

---

## ✅ What's Been Done

### 1. SSL Certificate Generated ✓
- **Location**: `/home/bsm/WebApp/eDOMOS-v2.1/door_alarm_system/ssl/`
- **Certificate**: `ssl/cert.pem` (Public certificate)
- **Private Key**: `ssl/key.pem` (Private key)
- **Type**: Self-signed certificate
- **Validity**: 10 years (3650 days)
- **Valid Until**: October 20, 2035

### 2. Certificate Details
```
Subject: C=IN, ST=Maharashtra, L=Mumbai, O=BSM SciTech, OU=eDOMOS, CN=192.168.31.227
Issuer: C=IN, ST=Maharashtra, L=Mumbai, O=BSM SciTech, OU=eDOMOS, CN=192.168.31.227
Alternative Names: IP:192.168.31.227, IP:127.0.0.1, DNS:localhost
```

### 3. App Integration ✓
The Flask application (`app.py`) now:
- ✅ Automatically detects SSL certificates
- ✅ Enables HTTPS when certificates are found
- ✅ Falls back to HTTP if certificates are missing
- ✅ Configures WebSocket (WSS) for secure communication
- ✅ Displays SSL status on startup

---

## 🌐 Access URLs

### With SSL (HTTPS) - Current Setup
```
🔒 Main Application: https://192.168.31.227:5000
🔒 WebSocket: wss://192.168.31.227:5000/socket.io/
```

### Without SSL (HTTP) - Fallback
```
🌐 Main Application: http://192.168.31.227:5000
🌐 WebSocket: ws://192.168.31.227:5000/socket.io/
```

---

## 🚀 Starting the Application

### Option 1: Using the startup script (Recommended)
```bash
cd /home/bsm/WebApp/eDOMOS-v2.1/door_alarm_system
./run_app.sh
```

### Option 2: Direct Python execution
```bash
cd /home/bsm/WebApp/eDOMOS-v2.1/door_alarm_system
python app.py
```

Both methods will:
1. Check for SSL certificates
2. Enable HTTPS if certificates exist
3. Display the correct access URL
4. Start the server with appropriate protocol

---

## 🔄 Regenerating SSL Certificates

If you need to regenerate certificates (e.g., certificate expired or you want to change details):

```bash
cd /home/bsm/WebApp/eDOMOS-v2.1/door_alarm_system
./generate_ssl_cert.sh
```

The script will:
- Ask if you want to overwrite existing certificates
- Generate new 4096-bit RSA certificates
- Set proper permissions (600 for key, 644 for cert)
- Display certificate details

---

## ⚠️ Browser Security Warning

### Why do I see a security warning?

Because this is a **self-signed certificate** (not issued by a trusted Certificate Authority), browsers will show a security warning when you first access the site.

### How to proceed:

#### Chrome/Edge:
1. Click **"Advanced"**
2. Click **"Proceed to 192.168.31.227 (unsafe)"**

#### Firefox:
1. Click **"Advanced"**
2. Click **"Accept the Risk and Continue"**

#### Safari:
1. Click **"Show Details"**
2. Click **"visit this website"**
3. Click **"Visit Website"**

### ✅ Is it safe?

**YES!** The warning appears because the certificate is self-signed, not because of actual security issues. The connection is still encrypted with 4096-bit RSA encryption.

For **internal network use** (like your setup), self-signed certificates are perfectly acceptable and secure.

---

## 🔒 Security Features

### Encryption
- **Algorithm**: RSA 4096-bit
- **Protocol**: TLS/SSL
- **WebSocket**: Secure (WSS)

### What's Protected
✅ All login credentials encrypted
✅ Dashboard data transmission encrypted
✅ API calls encrypted
✅ WebSocket real-time updates encrypted
✅ File uploads encrypted
✅ Session cookies secured

---

## 🛠️ Troubleshooting

### Issue 1: Certificate Not Found

**Symptom**: App shows "SSL certificates not found - Running on HTTP"

**Solution**:
```bash
cd /home/bsm/WebApp/eDOMOS-v2.1/door_alarm_system
./generate_ssl_cert.sh
```

### Issue 2: Permission Denied

**Symptom**: "Permission denied" when starting app with SSL

**Solution**:
```bash
cd /home/bsm/WebApp/eDOMOS-v2.1/door_alarm_system
chmod 600 ssl/key.pem
chmod 644 ssl/cert.pem
```

### Issue 3: Port 5000 Already in Use

**Solution**:
```bash
lsof -ti:5000 | xargs kill -9
# Then restart the app
./run_app.sh
```

### Issue 4: WebSocket Not Connecting

**Issue**: WebSocket shows "connection refused" in browser console

**Solution**: Make sure you're using the correct protocol:
- If using HTTPS → Use `wss://` for WebSocket
- If using HTTP → Use `ws://` for WebSocket

The app automatically handles this, but if you've bookmarked the page, update the bookmark.

---

## 📱 Mobile/Remote Access

### From Mobile Device on Same Network

1. **Find Your Raspberry Pi IP**: `192.168.31.227`
2. **Open Browser**: Chrome, Safari, Firefox, etc.
3. **Navigate to**: `https://192.168.31.227:5000`
4. **Accept Security Warning** (one-time)
5. **Login**: admin / admin123

### From External Network (Internet)

To access from outside your local network, you'll need:
1. **Port Forwarding** on your router (forward port 5000)
2. **Dynamic DNS** (optional, for easy access)
3. **Stronger certificate** (recommended for internet exposure)

⚠️ **Security Note**: For internet exposure, consider using:
- Let's Encrypt certificates (free, trusted)
- VPN access instead of port forwarding
- Nginx reverse proxy with proper security headers

---

## 🔧 Advanced Configuration

### Custom Certificate Settings

Edit `generate_ssl_cert.sh` to customize:

```bash
# Change validity period (default 10 years)
DAYS_VALID=3650

# Change organization details
-subj "/C=IN/ST=Maharashtra/L=Mumbai/O=BSM SciTech/OU=eDOMOS/CN=192.168.31.227"

# Add more IP addresses
-addext "subjectAltName=IP:192.168.31.227,IP:127.0.0.1,IP:192.168.31.100"
```

### Using a Different Port

If you want to use a different port (e.g., 443 for standard HTTPS):

1. **Edit app.py**:
```python
# Change port=5000 to port=443
socketio.run(app, host='0.0.0.0', port=443, ...)
```

2. **Note**: Port 443 requires root/sudo:
```bash
sudo python app.py
```

---

## 📊 Verification

### Check Certificate Details
```bash
openssl x509 -in ssl/cert.pem -noout -text
```

### Check Certificate Expiry
```bash
openssl x509 -in ssl/cert.pem -noout -dates
```

### Test SSL Connection
```bash
openssl s_client -connect 192.168.31.227:5000
```

### Verify in Browser
1. Open `https://192.168.31.227:5000`
2. Click the **lock icon** in address bar
3. View certificate details

---

## 🎯 Production Deployment Recommendations

For production use, consider:

### 1. Use Trusted Certificates
- **Let's Encrypt** (free, automated)
- **Commercial CA** (Comodo, DigiCert, etc.)

### 2. Use Nginx Reverse Proxy
```nginx
server {
    listen 443 ssl http2;
    server_name 192.168.31.227;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 3. Enable HSTS (HTTP Strict Transport Security)
Add to app.py:
```python
@app.after_request
def set_security_headers(response):
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response
```

---

## 📋 Quick Reference Commands

```bash
# Generate new SSL certificate
./generate_ssl_cert.sh

# Start app (auto-detects SSL)
./run_app.sh

# Check certificate expiry
openssl x509 -in ssl/cert.pem -noout -enddate

# Restart app with SSL
lsof -ti:5000 | xargs kill -9 && ./run_app.sh

# View certificate details
openssl x509 -in ssl/cert.pem -noout -text

# Test HTTPS connection
curl -k https://192.168.31.227:5000

# Check SSL port
netstat -tlnp | grep :5000
```

---

## ✅ Current Status

- ✅ SSL Certificate: **Generated**
- ✅ App Integration: **Complete**
- ✅ HTTPS Access: **Enabled**
- ✅ WebSocket (WSS): **Enabled**
- ✅ Auto-detection: **Working**
- ✅ Fallback to HTTP: **Working**

---

## 🔗 Access Your Secure Application

```
🔒 HTTPS URL: https://192.168.31.227:5000
👤 Username: admin
🔑 Password: admin123
```

**Your eDOMOS system is now secured with SSL/TLS encryption! 🎉**
