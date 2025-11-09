# HTTP vs HTTPS Mode - Usage Guide

## 🌐 Overview

The eDOMOS Door Alarm System now supports **BOTH** HTTP and HTTPS modes with easy switching between them.

- **HTTP Mode**: Default, no certificate warnings, instant access ✅
- **HTTPS Mode**: Encrypted, secure (self-signed certificate) 🔐

---

## 🚀 Quick Start

### HTTP Mode (Default - Recommended for Local Network)

```bash
# Option 1: Default (no arguments)
./run_app.sh

# Option 2: Explicit HTTP flag
./run_app.sh --http

# Option 3: Direct Python with environment variable
USE_SSL=false python app.py
```

**Access URL**: `http://192.168.31.227:5000`

✅ **Advantages**:
- No browser security warnings
- Instant access, no certificate issues
- Perfect for local network testing
- Works on all browsers immediately

---

### HTTPS Mode (Optional - For Production/Secure Deployments)

```bash
# Option 1: Using run_app.sh
./run_app.sh --https

# Option 2: Direct Python with environment variable
USE_SSL=true python app.py

# Option 3: Export variable first
export USE_SSL=true
python app.py
```

**Access URL**: `https://192.168.31.227:5000`

⚠️ **First-time setup**: You'll see browser security warning (expected for self-signed certificate)

**Bypassing Browser Warning**:

1. **Chrome/Edge**:
   - Click "Advanced"
   - Click "Proceed to 192.168.31.227 (unsafe)"

2. **Firefox**:
   - Click "Advanced"
   - Click "Accept the Risk and Continue"

3. **Safari**:
   - Click "Show Details"
   - Click "visit this website"

✅ **Advantages**:
- Encrypted data transmission
- Secure authentication
- WebSocket over SSL (wss://)
- Production-ready

---

## 🔐 SSL Certificate Management

### Generate SSL Certificates

```bash
./generate_ssl_cert.sh
```

This creates:
- `ssl/cert.pem` (SSL certificate - 10 year validity)
- `ssl/key.pem` (Private key)

**Certificate Details**:
- Organization: BSM SciTech
- Location: Mumbai, Maharashtra, India
- Common Name: 192.168.31.227
- Valid: 2025-2035 (10 years)

---

## 📊 Mode Comparison

| Feature | HTTP Mode | HTTPS Mode |
|---------|-----------|------------|
| **Browser Warnings** | ❌ None | ⚠️ Self-signed cert warning |
| **Setup Complexity** | 🟢 Simple | 🟡 One-time certificate acceptance |
| **Data Encryption** | ❌ No | ✅ Yes (TLS 1.2+) |
| **WebSocket Protocol** | ws:// | wss:// |
| **Production Ready** | 🟡 Local only | ✅ Yes |
| **Performance** | 🟢 Slightly faster | 🟢 Negligible difference |

---

## 🛠️ Troubleshooting

### "SSL disabled - HTTP mode (default)" Message

✅ **This is normal!** HTTP is the default mode for convenience.

To use HTTPS: `./run_app.sh --https`

### "SSL Certificates not found" Error

**Solution**: Generate certificates first
```bash
./generate_ssl_cert.sh
./run_app.sh --https
```

### Browser Shows "ERR_CERT_AUTHORITY_INVALID"

⚠️ **This is expected** for self-signed certificates.

**Options**:
1. Click "Advanced" → "Proceed to site" (one-time per browser)
2. Use HTTP mode instead: `./run_app.sh --http`

### WebSocket Not Connecting

Check protocol matches:
- HTTP mode: `ws://192.168.31.227:5000/socket.io/`
- HTTPS mode: `wss://192.168.31.227:5000/socket.io/`

The application automatically uses the correct protocol.

---

## 🎯 Recommended Usage

### Development/Testing (Local Network)
```bash
./run_app.sh
# or
./run_app.sh --http
```
✅ No certificate warnings, instant access

### Production Deployment
```bash
./run_app.sh --https
```
✅ Encrypted communication, secure authentication

### Public Internet (with domain)
Use **Let's Encrypt** for trusted certificates:
```bash
# Example with certbot (requires domain name)
sudo certbot certonly --standalone -d yourdomain.com
# Copy certificates to ssl/ directory
cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem ssl/cert.pem
cp /etc/letsencrypt/live/yourdomain.com/privkey.pem ssl/key.pem
./run_app.sh --https
```

---

## 📱 Mobile Access

### HTTP Mode
Works immediately on all devices:
- Android: `http://192.168.31.227:5000`
- iOS: `http://192.168.31.227:5000`

### HTTPS Mode
Requires one-time certificate acceptance:
1. Open `https://192.168.31.227:5000` in mobile browser
2. Tap "Advanced" → "Proceed"
3. Bookmark for future use

---

## 🔄 Switching Between Modes

You can switch modes anytime **without restarting the server**:

```bash
# Stop current instance
pkill -f "python app.py"

# Start in desired mode
./run_app.sh --http   # or --https
```

---

## 💡 Environment Variable Control

For advanced users:

```bash
# Set environment variable
export USE_SSL=true   # Enable HTTPS
export USE_SSL=false  # Enable HTTP (default)

# Run application
python app.py
```

The `USE_SSL` environment variable overrides all other settings.

---

## 🔍 Server Startup Messages

### HTTP Mode (Default)
```
🌐 SSL disabled - HTTP mode (default)
💡 To enable HTTPS: USE_SSL=true python app.py
🌐 Server will be available at: http://0.0.0.0:5000
🔌 WebSocket endpoint: ws://0.0.0.0:5000/socket.io/
```

### HTTPS Mode
```
🔐 SSL enabled - HTTPS mode
🌐 Server will be available at: https://0.0.0.0:5000
🔌 WebSocket endpoint: wss://0.0.0.0:5000/socket.io/
🔒 SSL Certificate: .../ssl/cert.pem
🔑 SSL Private Key: .../ssl/key.pem
⚠️  Self-signed certificate - Browser will show security warning
```

### No Certificates Found
```
⚠️  SSL certificates not found - Running on HTTP
💡 Run './generate_ssl_cert.sh' to generate SSL certificates
```

---

## 📚 Additional Resources

- **SSL Configuration Guide**: `SSL_CONFIGURATION_GUIDE.md`
- **Endpoint Testing Guide**: `ACTUAL_ENDPOINTS_FOR_TESTING.md`
- **Product Documentation**: Available in Help menu

---

## ❓ FAQ

**Q: Which mode should I use?**
A: For local network testing → HTTP. For production/internet → HTTPS.

**Q: Is HTTP mode insecure?**
A: On a trusted local network (home/office), HTTP is fine. For internet access, use HTTPS.

**Q: Can I use a trusted SSL certificate?**
A: Yes! Replace `ssl/cert.pem` and `ssl/key.pem` with your trusted certificates.

**Q: How do I make the browser trust my self-signed certificate?**
A: Add it to your system's trusted certificates, or use HTTP mode for local access.

**Q: Does the app work differently in HTTP vs HTTPS?**
A: No! All features work identically. Only the transport encryption differs.

---

## 📞 Support

For issues or questions:
- Check the troubleshooting section above
- Review `SSL_CONFIGURATION_GUIDE.md`
- Contact: BSM SciTech

---

**Last Updated**: October 2024  
**Version**: eDOMOS v2.1
