#!/bin/bash
# SSL Test Script for eDOMOS v2.1

echo "🔐 SSL Certificate Test for eDOMOS v2.1"
echo "========================================"
echo ""

SSL_DIR="/home/bsm/WebApp/eDOMOS-v2.1/door_alarm_system/ssl"

# Test 1: Check if certificates exist
echo "📋 Test 1: Certificate Files"
if [ -f "$SSL_DIR/cert.pem" ]; then
    echo "✅ Certificate found: $SSL_DIR/cert.pem"
else
    echo "❌ Certificate NOT found"
    exit 1
fi

if [ -f "$SSL_DIR/key.pem" ]; then
    echo "✅ Private key found: $SSL_DIR/key.pem"
else
    echo "❌ Private key NOT found"
    exit 1
fi

echo ""

# Test 2: Check certificate validity
echo "📋 Test 2: Certificate Validity"
EXPIRY=$(openssl x509 -in "$SSL_DIR/cert.pem" -noout -enddate | cut -d= -f2)
echo "📅 Expires: $EXPIRY"

# Check if certificate is valid
if openssl x509 -in "$SSL_DIR/cert.pem" -noout -checkend 0 >/dev/null 2>&1; then
    echo "✅ Certificate is valid"
else
    echo "❌ Certificate has expired"
    exit 1
fi

echo ""

# Test 3: Check certificate details
echo "📋 Test 3: Certificate Details"
openssl x509 -in "$SSL_DIR/cert.pem" -noout -subject -issuer
echo ""

# Test 4: Check file permissions
echo "📋 Test 4: File Permissions"
CERT_PERM=$(stat -c "%a" "$SSL_DIR/cert.pem")
KEY_PERM=$(stat -c "%a" "$SSL_DIR/key.pem")

echo "Certificate permissions: $CERT_PERM"
if [ "$CERT_PERM" = "644" ]; then
    echo "✅ Certificate permissions correct"
else
    echo "⚠️  Certificate permissions should be 644"
fi

echo "Private key permissions: $KEY_PERM"
if [ "$KEY_PERM" = "600" ]; then
    echo "✅ Private key permissions correct"
else
    echo "⚠️  Private key permissions should be 600"
fi

echo ""

# Test 5: Check if app detects SSL
echo "📋 Test 5: App SSL Detection"
cd /home/bsm/WebApp/eDOMOS-v2.1/door_alarm_system

# Check if app.py has SSL code
if grep -q "SSL_CERT" app.py; then
    echo "✅ App has SSL detection code"
else
    echo "❌ App missing SSL detection code"
    exit 1
fi

echo ""

# Test 6: Try to start server briefly (kills after 3 seconds)
echo "📋 Test 6: SSL Server Test"
echo "Starting server for 3 seconds..."

# Start app in background
python app.py > /tmp/ssl_test.log 2>&1 &
APP_PID=$!

# Wait 3 seconds
sleep 3

# Check if "SSL" appears in logs
if grep -q "SSL" /tmp/ssl_test.log; then
    echo "✅ Server started with SSL enabled"
    cat /tmp/ssl_test.log | grep -E "(SSL|https|wss)" | head -3
else
    echo "⚠️  Server started without SSL"
    cat /tmp/ssl_test.log | head -5
fi

# Kill the test server
kill $APP_PID 2>/dev/null
lsof -ti:5000 | xargs kill -9 2>/dev/null

echo ""
echo "========================================"
echo "✅ SSL Certificate Tests Complete!"
echo ""
echo "🌐 Access your secure app at:"
echo "   https://192.168.31.227:5000"
echo ""
echo "⚠️  Remember: Browser will show security warning"
echo "   (This is normal for self-signed certificates)"
