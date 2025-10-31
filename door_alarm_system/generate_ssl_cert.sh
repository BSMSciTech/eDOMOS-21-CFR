#!/bin/bash
# SSL Certificate Generation Script for eDOMOS v2.1
# This script generates a self-signed SSL certificate for HTTPS

CERT_DIR="/home/bsm/WebApp/eDOMOS-v2.1/door_alarm_system/ssl"
DAYS_VALID=3650  # 10 years

echo "🔐 Generating SSL Certificate for eDOMOS v2.1..."
echo "=================================================="

# Create ssl directory if it doesn't exist
mkdir -p "$CERT_DIR"

# Check if certificates already exist
if [ -f "$CERT_DIR/cert.pem" ] && [ -f "$CERT_DIR/key.pem" ]; then
    echo "⚠️  SSL certificates already exist!"
    echo "📁 Location: $CERT_DIR"
    echo ""
    read -p "Do you want to regenerate certificates? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "✅ Using existing certificates"
        exit 0
    fi
    echo "🔄 Regenerating certificates..."
fi

# Generate self-signed certificate
echo "📝 Creating self-signed SSL certificate..."
openssl req -x509 -newkey rsa:4096 -nodes \
    -out "$CERT_DIR/cert.pem" \
    -keyout "$CERT_DIR/key.pem" \
    -days $DAYS_VALID \
    -subj "/C=IN/ST=Maharashtra/L=Mumbai/O=BSM SciTech/OU=eDOMOS/CN=192.168.31.227" \
    -addext "subjectAltName=IP:192.168.31.227,IP:127.0.0.1,DNS:localhost"

# Check if generation was successful
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ SSL Certificate generated successfully!"
    echo "=================================================="
    echo "📁 Certificate Location: $CERT_DIR/cert.pem"
    echo "🔑 Private Key Location: $CERT_DIR/key.pem"
    echo "📅 Valid for: $DAYS_VALID days (~10 years)"
    echo ""
    echo "🌐 HTTPS URL: https://192.168.31.227:5000"
    echo ""
    echo "⚠️  NOTE: This is a self-signed certificate."
    echo "   Browsers will show a security warning on first access."
    echo "   Click 'Advanced' and 'Proceed to 192.168.31.227' to continue."
    echo ""
    echo "📋 Certificate Details:"
    openssl x509 -in "$CERT_DIR/cert.pem" -noout -subject -issuer -dates
    echo ""
    echo "=================================================="
    
    # Set proper permissions
    chmod 600 "$CERT_DIR/key.pem"
    chmod 644 "$CERT_DIR/cert.pem"
    
    echo "✅ Permissions set correctly"
    echo "🚀 You can now start the Flask app with SSL enabled!"
else
    echo ""
    echo "❌ Error: Failed to generate SSL certificate"
    echo "Please check if OpenSSL is installed: sudo apt-get install openssl"
    exit 1
fi
