#!/bin/bash
# ============================================================================
# eDOMOS Complete Startup Script
# Handles: process cleanup, GPIO reset, and server startup
# ============================================================================

set -e  # Exit on error

APP_DIR="/home/bsm/WebApp/eDOMOS-v2.1/door_alarm_system"
LOG_FILE="/tmp/edomos_https.log"
PID_FILE="/tmp/edomos.pid"

echo "============================================================"
echo "🚀 eDOMOS STARTUP SCRIPT"
echo "============================================================"
echo ""

# Function to kill existing processes
kill_existing_processes() {
    echo "[1/5] Checking for existing eDOMOS processes..."
    
    # Check if PID file exists
    if [ -f "$PID_FILE" ]; then
        OLD_PID=$(cat "$PID_FILE")
        if ps -p "$OLD_PID" > /dev/null 2>&1; then
            echo "  ├─ Found process with PID $OLD_PID (from PID file)"
            echo "  └─ Killing PID $OLD_PID..."
            sudo kill -9 "$OLD_PID" 2>/dev/null || true
            sleep 1
        fi
        rm -f "$PID_FILE"
    fi
    
    # Kill any python app.py processes
    PIDS=$(ps aux | grep -E "python.*app.py" | grep -v grep | awk '{print $2}')
    if [ -n "$PIDS" ]; then
        echo "  ├─ Found running app.py processes: $PIDS"
        for PID in $PIDS; do
            echo "  │   └─ Killing PID $PID..."
            sudo kill -9 "$PID" 2>/dev/null || true
        done
        sleep 2
    else
        echo "  └─ No existing app.py processes found"
    fi
    
    # Kill anything on port 5000
    PORT_PIDS=$(sudo lsof -ti:5000 2>/dev/null || true)
    if [ -n "$PORT_PIDS" ]; then
        echo "  ├─ Found processes on port 5000: $PORT_PIDS"
        sudo kill -9 $PORT_PIDS 2>/dev/null || true
        sleep 1
        echo "  └─ Port 5000 cleared"
    else
        echo "  └─ Port 5000 is free"
    fi
    
    echo ""
}

# Function to reset GPIO
reset_gpio() {
    echo "[2/5] Resetting GPIO pins..."
    cd "$APP_DIR"
    python3 gpio_reset.py
    echo ""
}

# Function to verify environment
verify_environment() {
    echo "[3/5] Verifying environment..."
    
    # Check if we're in the right directory
    if [ ! -f "$APP_DIR/app.py" ]; then
        echo "❌ Error: app.py not found in $APP_DIR"
        exit 1
    fi
    echo "  ├─ app.py found ✓"
    
    # Check Python version
    PYTHON_VERSION=$(python3 --version 2>&1)
    echo "  ├─ $PYTHON_VERSION ✓"
    
    # Check if instance directory exists
    if [ ! -d "$APP_DIR/instance" ]; then
        echo "  ├─ Creating instance directory..."
        mkdir -p "$APP_DIR/instance"
    fi
    echo "  ├─ Database directory exists ✓"
    
    # Check SSL certificates if HTTPS mode
    if [ "$USE_SSL" = "true" ]; then
        if [ -f "$APP_DIR/ssl/cert.pem" ] && [ -f "$APP_DIR/ssl/key.pem" ]; then
            echo "  ├─ SSL certificates found ✓"
            echo "  └─ Mode: HTTPS 🔐"
        else
            echo "  ├─ SSL certificates NOT found ⚠️"
            echo "  └─ Falling back to HTTP mode"
            export USE_SSL="false"
        fi
    else
        echo "  └─ Mode: HTTP 🌐"
    fi
    
    echo ""
}

# Function to start the server
start_server() {
    echo "[4/5] Starting eDOMOS server..."
    cd "$APP_DIR"
    
    # Start server in background and save PID
    if [ "$USE_SSL" = "true" ]; then
        echo "  ├─ Starting with HTTPS/SSL..."
        USE_SSL=true nohup python3 app.py > "$LOG_FILE" 2>&1 &
    else
        echo "  ├─ Starting with HTTP..."
        nohup python3 app.py > "$LOG_FILE" 2>&1 &
    fi
    
    # Save PID
    SERVER_PID=$!
    echo "$SERVER_PID" > "$PID_FILE"
    echo "  ├─ Server PID: $SERVER_PID"
    echo "  └─ Log file: $LOG_FILE"
    
    echo ""
}

# Function to verify startup
verify_startup() {
    echo "[5/5] Verifying server startup..."
    
    # Wait longer for full initialization (GPIO, audio, database)
    echo "  ├─ Waiting for initialization..."
    sleep 2
    
    # Check if process is still running
    if ps -p $(cat "$PID_FILE") > /dev/null 2>&1; then
        echo "  ├─ Process is running ✓"
    else
        echo "  ├─ Process died! ✗"
        echo "  └─ Check logs: tail -50 $LOG_FILE"
        exit 1
    fi
    
    # Check if port 5000 is listening (retry up to 3 times)
    PORT_READY=false
    for i in {1..3}; do
        sleep 2
        if sudo lsof -i:5000 > /dev/null 2>&1; then
            PORT_READY=true
            break
        fi
        if [ $i -lt 3 ]; then
            echo "  ├─ Port check $i/3: Still initializing..."
        fi
    done
    
    if [ "$PORT_READY" = true ]; then
        echo "  ├─ Port 5000 is listening ✓"
    else
        echo "  ├─ Port 5000 not listening after 8 seconds ⚠️"
        echo "  └─ Server may need more time or check logs for errors"
    fi
    
    echo ""
}

# Main execution
main() {
    kill_existing_processes
    reset_gpio
    verify_environment
    start_server
    verify_startup
    
    echo "============================================================"
    echo "✅ eDOMOS SERVER STARTED SUCCESSFULLY"
    echo "============================================================"
    echo ""
    echo "📋 Server Information:"
    echo "  ├─ PID: $(cat $PID_FILE)"
    if [ "$USE_SSL" = "true" ]; then
        echo "  ├─ URL: https://192.168.31.227:5000"
        echo "  ├─ Mode: HTTPS (Secure) 🔐"
    else
        echo "  ├─ URL: http://192.168.31.227:5000"
        echo "  ├─ Mode: HTTP 🌐"
    fi
    echo "  ├─ Logs: $LOG_FILE"
    echo "  └─ Status: Running ✓"
    echo ""
    echo "📝 Management Commands:"
    echo "  ├─ View logs: tail -f $LOG_FILE"
    echo "  ├─ Stop server: ./stop.sh"
    echo "  └─ Restart: ./start.sh"
    echo ""
    echo "============================================================"
}

# Run main function
main
