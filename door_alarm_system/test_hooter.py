#!/usr/bin/env python3
"""
Quick test script for IRLZ44N MOSFET hooter control
Tests GPIO Pin 10 (BOARD numbering) for 12V hooter siren
"""

import RPi.GPIO as GPIO
import time
import sys

# Pin configuration
HOOTER_PIN = 10  # Physical Pin 10 (GPIO 15)

def test_hooter_direct():
    """Direct test of hooter MOSFET control"""
    print("🔊 Starting hooter MOSFET test...")
    
    try:
        # Initialize GPIO
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(HOOTER_PIN, GPIO.OUT)
        
        print(f"📍 Using Pin {HOOTER_PIN} for MOSFET gate control")
        print("🔧 Ensure your circuit is connected:")
        print("   - Pin 10 → 10kΩ → MOSFET Gate")
        print("   - MOSFET Gate → 100Ω → GND")
        print("   - MOSFET Drain → Hooter (+)")
        print("   - MOSFET Source → GND")
        print("   - 12V (+) → Hooter (+)")
        print("   - 12V (-) → GND")
        print()
        
        # Test sequence
        print("🔴 Step 1: Setting GPIO LOW (MOSFET OFF)")
        GPIO.output(HOOTER_PIN, GPIO.LOW)
        time.sleep(1)
        
        print("🟢 Step 2: Setting GPIO HIGH (MOSFET ON - Hooter should sound)")
        GPIO.output(HOOTER_PIN, GPIO.HIGH)
        time.sleep(2)  # 2-second test
        
        print("🔴 Step 3: Setting GPIO LOW (MOSFET OFF - Hooter should stop)")
        GPIO.output(HOOTER_PIN, GPIO.LOW)
        
        print("✅ Test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
    finally:
        try:
            GPIO.cleanup()
            print("🔧 GPIO cleanup completed")
        except:
            pass

if __name__ == "__main__":
    print("🚨 HOOTER MOSFET TEST")
    print("=" * 50)
    
    # Safety warning
    input("⚠️  WARNING: This will activate your 12V hooter siren!\nPress ENTER to continue or Ctrl+C to abort...")
    
    test_hooter_direct()