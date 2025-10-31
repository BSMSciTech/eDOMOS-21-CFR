#!/usr/bin/env python3
"""
GPIO Reset Script - Force release all GPIO pins
"""
import RPi.GPIO as GPIO
import time
import os
import signal
import subprocess

def kill_gpio_processes():
    """Kill any processes that might be using GPIO"""
    try:
        # Kill any python processes that might be using GPIO
        subprocess.run(['sudo', 'pkill', '-f', 'door_alarm'], stderr=subprocess.DEVNULL)
        subprocess.run(['sudo', 'pkill', '-f', 'app.py'], stderr=subprocess.DEVNULL)
        time.sleep(1)
        print("✅ Killed existing GPIO processes")
    except Exception as e:
        print(f"⚠️ Error killing processes: {e}")

def reset_gpio_pins():
    """Reset all GPIO pins used by the door alarm system"""
    pins = [11, 13, 16, 18, 22]  # All pins used by the system
    
    try:
        # Try different GPIO modes
        for mode in [GPIO.BOARD, GPIO.BCM]:
            try:
                GPIO.setmode(mode)
                GPIO.cleanup()
                print(f"✅ Cleanup successful with mode: {mode}")
                break
            except Exception as e:
                print(f"⚠️ Cleanup failed with mode {mode}: {e}")
                continue
        
        # Force setup and cleanup each pin individually
        GPIO.setmode(GPIO.BOARD)
        for pin in pins:
            try:
                GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)
                GPIO.output(pin, GPIO.LOW)
                print(f"✅ Reset pin {pin}")
            except Exception as e:
                print(f"⚠️ Failed to reset pin {pin}: {e}")
        
        # Final cleanup
        GPIO.cleanup()
        print("✅ Final GPIO cleanup completed")
        
    except Exception as e:
        print(f"❌ GPIO reset error: {e}")

def check_gpio_permissions():
    """Check if user has GPIO permissions"""
    try:
        # Check if user is in gpio group
        import grp
        gpio_group = grp.getgrnam('gpio')
        current_user = os.getenv('USER')
        
        if current_user in gpio_group.gr_mem:
            print(f"✅ User {current_user} is in gpio group")
        else:
            print(f"⚠️ User {current_user} is NOT in gpio group")
            print("   Run: sudo usermod -a -G gpio $USER")
            print("   Then logout and login again")
            
    except Exception as e:
        print(f"⚠️ Could not check GPIO permissions: {e}")

if __name__ == "__main__":
    print("🔧 GPIO Reset Script Starting...")
    
    kill_gpio_processes()
    time.sleep(1)
    
    check_gpio_permissions()
    
    reset_gpio_pins()
    
    print("🔧 GPIO Reset Complete!")
    print("   You can now try running: python3 app.py")