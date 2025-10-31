#!/bin/bash
# BSM Door Alarm System - Run Script for REAL HARDWARE
# Run this script when you want the LEDs and GPIO to work

echo "🚀 Starting BSM Door Alarm System for REAL HARDWARE..."
echo "📁 Switching to app directory..."
cd "$(dirname "$0")"

echo "🐍 Activating Python virtual environment..."
source venv/bin/activate

echo "🔧 Setting up environment variables..."
# Add system pandas to Python path for virtual environment
export PYTHONPATH="/usr/lib/python3/dist-packages:$PYTHONPATH"

# DO NOT set TESTING=1 - we want real GPIO control
echo "⚡ REAL HARDWARE MODE - GPIO and LEDs will be active"

echo "🌐 Starting Flask-SocketIO web server..."
echo "📡 Server will be available at: http://localhost:5000"
echo "🔌 WebSocket endpoint: ws://localhost:5000/socket.io/"
echo "👤 Default login: admin / admin"
echo ""
echo "🔴🟢⚪ LEDs should turn on when system starts"
echo "Press Ctrl+C to stop the server"
echo "=================================="

python app.py