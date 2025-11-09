#!/usr/bin/env python3
"""
Simple test script to manually test the white LED (Pin 16)
This will help diagnose if the LED hardware is working correctly.
"""

import time
import sys

try:
    import RPi.GPIO as GPIO
    print("✅ GPIO library imported successfully")
except ImportError:
    print("❌ RPi.GPIO library not found!")
    sys.exit(1)

def test_white_led():
    """Test the white LED by turning it on and off"""
    
    try:
        print("🔧 Setting up GPIO...")
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        
        # Setup white LED pin (Pin 16)
        GPIO.setup(16, GPIO.OUT)
        print("✅ GPIO Pin 16 (White LED) configured as output")
        
        print("\n🔍 Testing White LED (Pin 16)...")
        print("This will blink the white LED 5 times")
        print("Watch the physical LED to see if it lights up!")
        
        for i in range(5):
            print(f"\n🔴 Blink #{i+1}: LED ON")
            GPIO.output(16, GPIO.HIGH)
            
            # Verify the pin state
            pin_state = GPIO.input(16)
            print(f"📊 Pin 16 state: {pin_state} (should be 1)")
            
            time.sleep(2)  # LED on for 2 seconds
            
            print(f"⚫ Blink #{i+1}: LED OFF")
            GPIO.output(16, GPIO.LOW)
            
            # Verify the pin state
            pin_state = GPIO.input(16)
            print(f"📊 Pin 16 state: {pin_state} (should be 0)")
            
            time.sleep(1)  # LED off for 1 second
        
        print("\n✅ LED test completed!")
        print("\nDid you see the white LED blinking?")
        print("If NO:")
        print("  - Check LED is connected to GPIO Pin 16")
        print("  - Check LED polarity (longer leg to positive)")
        print("  - Check if LED is burned out")
        print("  - Check resistor connection")
        
    except Exception as e:
        print(f"❌ Error during LED test: {e}")
    
    finally:
        try:
            GPIO.cleanup()
            print("🧹 GPIO cleanup completed")
        except:
            pass

def test_all_leds():
    """Test all LEDs in sequence"""
    
    try:
        print("🔧 Setting up GPIO for all LEDs...")
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        
        # Setup all LED pins
        led_pins = {
            22: "Green LED",
            13: "Red LED", 
            16: "White LED"
        }
        
        for pin, name in led_pins.items():
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)  # Start with all LEDs off
            print(f"✅ {name} (Pin {pin}) configured")
        
        print("\n🌈 Testing all LEDs in sequence...")
        
        for pin, name in led_pins.items():
            print(f"\n🔍 Testing {name} (Pin {pin})")
            
            # Turn on this LED
            GPIO.output(pin, GPIO.HIGH)
            print(f"🔴 {name} ON")
            
            # Verify state
            state = GPIO.input(pin)
            print(f"📊 Pin {pin} state: {state}")
            
            time.sleep(3)  # Keep on for 3 seconds
            
            # Turn off this LED
            GPIO.output(pin, GPIO.LOW)
            print(f"⚫ {name} OFF")
            
            time.sleep(1)
        
        print("\n✅ All LED tests completed!")
        
    except Exception as e:
        print(f"❌ Error during all LED test: {e}")
    
    finally:
        try:
            GPIO.cleanup()
            print("🧹 GPIO cleanup completed")
        except:
            pass

if __name__ == "__main__":
    print("🚨 eDOMOS White LED Test Script")
    print("=" * 40)
    
    choice = input("\nSelect test:\n1. White LED only\n2. All LEDs\nChoice (1 or 2): ").strip()
    
    if choice == "1":
        test_white_led()
    elif choice == "2":
        test_all_leds()
    else:
        print("❌ Invalid choice. Please run again and select 1 or 2.")