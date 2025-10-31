#!/bin/bash

# 🔒 Export mkcert Root CA for Browser Installation
# This script helps you export the Root CA certificate so you can install it on your devices

echo "🔐 mkcert Root CA Export Utility"
echo "=================================="
echo ""

# Get mkcert CA directory
CA_DIR=$(mkcert -CAROOT)

if [ ! -d "$CA_DIR" ]; then
    echo "❌ Error: mkcert CA directory not found!"
    echo "💡 Run: mkcert -install"
    exit 1
fi

# Check if rootCA.pem exists
if [ ! -f "$CA_DIR/rootCA.pem" ]; then
    echo "❌ Error: rootCA.pem not found in $CA_DIR"
    exit 1
fi

echo "✅ Found Root CA certificate:"
echo "   Location: $CA_DIR/rootCA.pem"
echo "   Size: $(du -h "$CA_DIR/rootCA.pem" | cut -f1)"
echo ""

# Create exports directory
EXPORT_DIR="$HOME/mkcert_export"
mkdir -p "$EXPORT_DIR"

# Copy Root CA to export directory
cp "$CA_DIR/rootCA.pem" "$EXPORT_DIR/rootCA.pem"
chmod 644 "$EXPORT_DIR/rootCA.pem"

echo "📤 Root CA copied to: $EXPORT_DIR/rootCA.pem"
echo ""

# Show certificate details
echo "📋 Certificate Details:"
echo "----------------------"
openssl x509 -in "$EXPORT_DIR/rootCA.pem" -text -noout | grep -A 3 "Issuer:"
echo ""
openssl x509 -in "$EXPORT_DIR/rootCA.pem" -text -noout | grep -A 2 "Validity"
echo ""

# Options menu
echo "🎯 Installation Options:"
echo "========================"
echo ""
echo "Option 1: HTTP Download (Temporary Web Server)"
echo "---------------------------------------------"
echo "Run this command to start a temporary web server:"
echo ""
echo "    cd $EXPORT_DIR && python3 -m http.server 8080"
echo ""
echo "Then on your device, go to: http://192.168.31.227:8080"
echo "Download 'rootCA.pem' and install it (see INSTALL_ROOT_CA.md)"
echo "Press Ctrl+C to stop the server when done."
echo ""
echo ""
echo "Option 2: SCP/SFTP Transfer"
echo "---------------------------"
echo "From your computer, run:"
echo ""
echo "    scp bsm@192.168.31.227:$EXPORT_DIR/rootCA.pem ~/Desktop/"
echo ""
echo "Then install the certificate (see INSTALL_ROOT_CA.md)"
echo ""
echo ""
echo "Option 3: USB Transfer"
echo "----------------------"
echo "Copy this file to a USB drive:"
echo "    $EXPORT_DIR/rootCA.pem"
echo ""
echo ""
echo "📖 Full Installation Guide:"
echo "============================="
echo "See: ~/WebApp/eDOMOS-v2.1/door_alarm_system/INSTALL_ROOT_CA.md"
echo ""
echo "Quick guide by OS:"
echo "  • Windows: Double-click → Trusted Root CA → Restart browser"
echo "  • macOS: Double-click → Keychain → Trust → Restart browser"
echo "  • Linux: sudo cp to /usr/local/share/ca-certificates/ → update-ca-trust"
echo "  • Android: Settings → Security → Install CA certificate"
echo "  • iOS: Email certificate → Install Profile → Enable Trust"
echo ""
echo "✅ After installation, visit: https://192.168.31.227:5000"
echo "   You should see a green padlock with no warnings!"
echo ""

# Ask if user wants to start web server
read -p "🚀 Start temporary web server now? (y/n): " choice
if [[ "$choice" == "y" || "$choice" == "Y" ]]; then
    echo ""
    echo "📡 Starting web server on http://192.168.31.227:8080"
    echo "📱 Go to this URL on your device to download rootCA.pem"
    echo "⏹️  Press Ctrl+C when done"
    echo ""
    cd "$EXPORT_DIR" && python3 -m http.server 8080
else
    echo ""
    echo "👋 You can start it later with:"
    echo "   cd $EXPORT_DIR && python3 -m http.server 8080"
    echo ""
fi
