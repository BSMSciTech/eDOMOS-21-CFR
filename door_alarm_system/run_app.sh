#!/bin/bash
# BSM Door Alarm System - Run Script with HTTP/HTTPS Support
# Usage:
#   ./run_app.sh          - Run in HTTP mode (default, no SSL warnings)
#   ./run_app.sh --http   - Run in HTTP mode (explicit)
#   ./run_app.sh --https  - Run in HTTPS mode (requires SSL certificates)

echo "🚀 Starting BSM Door Alarm System..."
echo "📁 Switching to app directory..."
cd "$(dirname "$0")"

# Parse command-line arguments
USE_SSL="false"
if [ "$1" == "--https" ]; then
    USE_SSL="true"
    echo "🔐 HTTPS mode requested"
elif [ "$1" == "--http" ]; then
    USE_SSL="false"
    echo "🌐 HTTP mode requested (explicit)"
elif [ -n "$1" ]; then
    echo "❌ Invalid argument: $1"
    echo "Usage: $0 [--http | --https]"
    echo "  --http   Run in HTTP mode (default)"
    echo "  --https  Run in HTTPS mode"
    exit 1
else
    echo "🌐 HTTP mode (default)"
fi

# Check if SSL certificates exist (for HTTPS mode)
if [ "$USE_SSL" == "true" ]; then
    if [ -f "ssl/cert.pem" ] && [ -f "ssl/key.pem" ]; then
        echo "✅ SSL Certificates found - HTTPS enabled"
        SERVER_URL="https://192.168.31.227:5000"
        WS_URL="wss://192.168.31.227:5000/socket.io/"
    else
        echo "❌ SSL Certificates not found!"
        echo "💡 Run './generate_ssl_cert.sh' to generate SSL certificates"
        echo "🌐 Falling back to HTTP mode"
        USE_SSL="false"
        SERVER_URL="http://192.168.31.227:5000"
        WS_URL="ws://192.168.31.227:5000/socket.io/"
    fi
else
    SERVER_URL="http://192.168.31.227:5000"
    WS_URL="ws://192.168.31.227:5000/socket.io/"
fi

echo "🐍 Activating Python virtual environment..."
source venv/bin/activate

echo "🔧 Setting up environment variables..."
# Add system pandas to Python path for virtual environment
export PYTHONPATH="/usr/lib/python3/dist-packages:$PYTHONPATH"

# Set SSL mode via environment variable
export USE_SSL="$USE_SSL"

# Set TESTING=1 if you're not on Raspberry Pi hardware 
# (comment out the next line if running on actual Pi)
export TESTING=1

echo "🌐 Starting Flask-SocketIO web server..."
echo "📡 Server will be available at: $SERVER_URL"
echo "🔌 WebSocket endpoint: $WS_URL"
echo "👤 Default login: admin / admin"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=================================="

python app.py