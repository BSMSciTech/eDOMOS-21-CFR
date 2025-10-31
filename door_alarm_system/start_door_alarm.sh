#!/bin/bash

# Door Alarm System Startup Script
# Run this on your Raspberry Pi

echo "🚀 Starting eDOMOS Door Alarm System..."

# Kill any existing app processes
pkill -f "python.*app" 2>/dev/null

# Wait for cleanup
sleep 2

# Change to app directory
cd /home/bsm/WebApp/eDOMOS-v2.1/door_alarm_system

# Start the app with proper logging
echo "Starting Flask app..."
nohup python3 app.py > /tmp/door_alarm.log 2>&1 &

# Wait for startup
sleep 5

# Check if running
if pgrep -f "python.*app" > /dev/null; then
    echo "✅ Door alarm app is running!"
    echo "📱 Access from any device on your network:"
    echo "   → http://192.168.31.227:5000"
    echo "📊 Local access:"
    echo "   → http://127.0.0.1:5000"
    echo ""
    echo "📋 To check logs: tail -f /tmp/door_alarm.log"
    echo "🛑 To stop: pkill -f 'python.*app'"
else
    echo "❌ Failed to start app. Check logs:"
    echo "   tail /tmp/door_alarm.log"
fi