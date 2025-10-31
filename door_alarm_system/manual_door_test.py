#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time

# GPIO pins - must match main app.py
DOOR_SENSOR_PIN = 11

def simulate_door_open():
    """Simulate door opening by setting the sensor pin HIGH (NO sensor mode)"""
    print("🚪 Simulating door OPEN (setting pin HIGH)")
    print("   This will trigger the door alarm system...")
    print("   The alarm should trigger after 15 seconds")
    print("\n   Press Ctrl+C to stop simulation")
    
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(DOOR_SENSOR_PIN, GPIO.OUT)
    
    try:
        # Pull pin HIGH to simulate door open (NO sensor: HIGH = door open)
        GPIO.output(DOOR_SENSOR_PIN, GPIO.HIGH)
        print("🔴 Door sensor: OPEN (HIGH)")
        
        # Keep door "open" for 20 seconds to test alarm
        for i in range(20):
            print(f"⏰ Door open for {i+1} seconds...")
            time.sleep(1)
            
        print("\n🚪 Simulating door CLOSE")
        GPIO.output(DOOR_SENSOR_PIN, GPIO.LOW)
        print("🟢 Door sensor: CLOSED (LOW)")
        
    except KeyboardInterrupt:
        print("\n⏹️ Simulation stopped by user")
        GPIO.output(DOOR_SENSOR_PIN, GPIO.LOW)
        print("🟢 Door sensor: CLOSED (LOW)")
    finally:
        GPIO.cleanup()
        print("🧹 GPIO cleaned up")

if __name__ == "__main__":
    simulate_door_open()
