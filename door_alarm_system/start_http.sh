#!/bin/bash
# Start eDOMOS Door Alarm System in HTTP mode

cd "$(dirname "$0")"

# Kill any existing instances
pkill -f "python.*app.py"
sleep 2

# Start HTTP server
echo "🚀 Starting eDOMOS in HTTP mode..."
nohup python app.py > /tmp/edomos_http.log 2>&1 &

sleep 3

# Check if server started
if curl -s http://localhost:5000/api/test/ping > /dev/null; then
    echo "✅ HTTP server started successfully!"
    echo "📍 Access at: http://192.168.31.227:5000"
    echo "📋 Logs at: /tmp/edomos_http.log"
else
    echo "❌ Failed to start HTTP server. Check logs: tail -f /tmp/edomos_http.log"
    exit 1
fi
