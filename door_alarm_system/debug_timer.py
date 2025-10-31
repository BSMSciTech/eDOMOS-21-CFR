#!/usr/bin/env python3
"""
Debug Timer Issues - Test the alarm_timer function directly
"""
import sys
import time
import threading
import os
sys.path.insert(0, '/home/bsm/WebApp/eDOMOS-v2/eDOMOS-v2.1/door_alarm_system')

# Set testing environment to avoid GPIO
os.environ['TESTING'] = '1'

from app import app, db, Setting, alarm_timer

# Global variables for testing
timer_active = True
door_open = True
alarm_active = False

def test_timer_function():
    """Test the alarm_timer function directly"""
    print("🔍 TESTING ALARM TIMER FUNCTION")
    print("=" * 50)
    
    # Get timer duration from database
    with app.app_context():
        timer_setting = Setting.query.filter_by(key='timer_duration').first()
        duration = int(timer_setting.value) if timer_setting else 30
        
    print(f"📊 Timer Duration from DB: {duration} seconds")
    print(f"🚪 Door Open: {door_open}")
    print(f"⏰ Timer Active: {timer_active}")
    print()
    
    # Test the timer function
    print("🚀 Starting timer test...")
    start_time = time.time()
    
    # Call the alarm_timer function directly
    alarm_timer(duration)
    
    end_time = time.time()
    actual_duration = end_time - start_time
    
    print(f"\n📈 TEST RESULTS:")
    print(f"  ├─ Expected Duration: {duration} seconds")
    print(f"  ├─ Actual Duration: {actual_duration:.2f} seconds")
    print(f"  ├─ Difference: {actual_duration - duration:.2f} seconds")
    print(f"  └─ Status: {'✅ PASS' if abs(actual_duration - duration) < 1 else '❌ FAIL'}")

if __name__ == "__main__":
    test_timer_function()
