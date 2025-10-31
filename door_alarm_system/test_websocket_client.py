#!/usr/bin/env python3
import socketio
import time

# Create a Socket.IO client
sio = socketio.SimpleClient()

try:
    print("🔌 Attempting to connect to WebSocket server...")
    sio.connect('http://localhost:5000/events')
    print("✅ Successfully connected to WebSocket!")
    
    # Keep connection alive for a few seconds
    print("⏳ Waiting for events...")
    time.sleep(5)
    
except Exception as e:
    print(f"❌ Connection failed: {e}")
    import traceback
    traceback.print_exc()
finally:
    print("🔌 Disconnecting...")
    try:
        sio.disconnect()
    except:
        pass
