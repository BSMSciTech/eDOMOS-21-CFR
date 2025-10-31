#!/bin/bash
# ============================================================================
# eDOMOS Stop Script
# Gracefully stops the eDOMOS server and cleans up resources
# ============================================================================

PID_FILE="/tmp/edomos.pid"
LOG_FILE="/tmp/edomos_https.log"

echo "============================================================"
echo "🛑 STOPPING eDOMOS SERVER"
echo "============================================================"
echo ""

# Function to stop server
stop_server() {
    echo "[1/3] Stopping server processes..."
    
    # Check PID file first
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo "  ├─ Found server PID from file: $PID"
            echo "  ├─ Sending SIGTERM (graceful shutdown)..."
            kill "$PID" 2>/dev/null || true
            
            # Wait for graceful shutdown
            for i in {1..5}; do
                if ! ps -p "$PID" > /dev/null 2>&1; then
                    echo "  ├─ Process stopped gracefully ✓"
                    break
                fi
                echo "  │   └─ Waiting... ($i/5)"
                sleep 1
            done
            
            # Force kill if still running
            if ps -p "$PID" > /dev/null 2>&1; then
                echo "  ├─ Process didn't stop, forcing kill..."
                sudo kill -9 "$PID" 2>/dev/null || true
                sleep 1
            fi
        fi
        rm -f "$PID_FILE"
        echo "  └─ PID file removed"
    fi
    
    # Find any remaining python app.py processes
    REMAINING_PIDS=$(ps aux | grep -E "python.*app.py" | grep -v grep | awk '{print $2}')
    if [ -n "$REMAINING_PIDS" ]; then
        echo "  ├─ Found additional processes: $REMAINING_PIDS"
        for PID in $REMAINING_PIDS; do
            echo "  │   └─ Killing PID $PID..."
            sudo kill -9 "$PID" 2>/dev/null || true
        done
        sleep 1
    fi
    
    echo ""
}

# Function to clear port 5000
clear_port() {
    echo "[2/3] Clearing port 5000..."
    
    PORT_PIDS=$(sudo lsof -ti:5000 2>/dev/null || true)
    if [ -n "$PORT_PIDS" ]; then
        echo "  ├─ Found processes on port 5000: $PORT_PIDS"
        sudo kill -9 $PORT_PIDS 2>/dev/null || true
        sleep 1
        echo "  └─ Port 5000 cleared ✓"
    else
        echo "  └─ Port 5000 is already free ✓"
    fi
    
    echo ""
}

# Function to verify shutdown
verify_shutdown() {
    echo "[3/3] Verifying shutdown..."
    
    # Check for any remaining processes
    if ps aux | grep -E "python.*app.py" | grep -v grep > /dev/null; then
        echo "  ├─ WARNING: Some processes still running ⚠️"
        echo "  └─ Run: ps aux | grep app.py"
    else
        echo "  ├─ No app.py processes running ✓"
    fi
    
    # Check port 5000
    if sudo lsof -i:5000 > /dev/null 2>&1; then
        echo "  └─ WARNING: Port 5000 still in use ⚠️"
    else
        echo "  └─ Port 5000 is free ✓"
    fi
    
    echo ""
}

# Main execution
main() {
    stop_server
    clear_port
    verify_shutdown
    
    echo "============================================================"
    echo "✅ eDOMOS SERVER STOPPED"
    echo "============================================================"
    echo ""
    echo "To restart: ./start.sh"
    echo ""
}

# Run main function
main
