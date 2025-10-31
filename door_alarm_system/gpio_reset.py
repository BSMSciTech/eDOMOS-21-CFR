#!/usr/bin/env python3
"""
GPIO Reset Utility for eDOMOS
Forcefully resets all GPIO pins and clears any stuck states
"""

import RPi.GPIO as GPIO
import time
import sys

def reset_gpio():
    """Completely reset GPIO to clean state"""
    print("=" * 60)
    print("🔧 GPIO RESET UTILITY")
    print("=" * 60)
    
    # Disable warnings
    GPIO.setwarnings(False)
    
    # Multiple cleanup attempts with different modes
    print("\n[1/5] Attempting GPIO cleanup (BCM mode)...")
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.cleanup()
        print("✅ BCM mode cleanup successful")
    except Exception as e:
        print(f"⚠️  BCM mode cleanup: {e}")
    
    time.sleep(0.3)
    
    print("\n[2/5] Attempting GPIO cleanup (BOARD mode)...")
    try:
        GPIO.setmode(GPIO.BOARD)
        GPIO.cleanup()
        print("✅ BOARD mode cleanup successful")
    except Exception as e:
        print(f"⚠️  BOARD mode cleanup: {e}")
    
    time.sleep(0.3)
    
    print("\n[3/5] Force cleanup specific pins...")
    # Pins used by eDOMOS (BOARD numbering)
    edomos_pins = [11, 13, 16, 18, 22]
    for pin in edomos_pins:
        try:
            GPIO.cleanup(pin)
            print(f"✅ Pin {pin} cleaned")
        except Exception as e:
            print(f"⚠️  Pin {pin}: {e}")
        time.sleep(0.05)
    
    time.sleep(0.3)
    
    print("\n[4/5] Reset GPIO mode to BOARD...")
    try:
        GPIO.setmode(GPIO.BOARD)
        print("✅ GPIO mode set to BOARD")
    except Exception as e:
        print(f"⚠️  Mode set: {e}")
    
    time.sleep(0.3)
    
    print("\n[5/5] Final cleanup...")
    try:
        GPIO.cleanup()
        print("✅ Final cleanup successful")
    except Exception as e:
        print(f"⚠️  Final cleanup: {e}")
    
    print("\n" + "=" * 60)
    print("✅ GPIO RESET COMPLETE")
    print("=" * 60)
    print("\nYou can now start app.py")

if __name__ == '__main__':
    try:
        reset_gpio()
    except KeyboardInterrupt:
        print("\n\n⚠️  Reset interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
