#!/usr/bin/env python3
"""
Comprehensive test for eDOMOS-v2.1 system
This test will verify:
1. Timer duration setting
2. Alarm timing accuracy
3. LED behavior
4. Audio functionality
"""
import os
import sys
import time
import threading
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, '/home/bsm/WebApp/eDOMOS-v2/eDOMOS-v2.1/door_alarm_system')

# Set testing mode initially
os.environ['TESTING'] = '1'

def test_database_settings():
    """Test 1: Verify database settings"""
    print("🔍 TEST 1: Database Settings")
    print("-" * 30)
    
    try:
        from app import app, db, Setting
        with app.app_context():
            timer_setting = Setting.query.filter_by(key='timer_duration').first()
            if timer_setting:
                print(f"✅ Timer Duration: {timer_setting.value} seconds")
                return int(timer_setting.value)
            else:
                print("❌ No timer setting found")
                return None
    except Exception as e:
        print(f"❌ Database error: {e}")
        return None

def test_timer_function():
    """Test 2: Test the alarm_timer function directly"""
    print("\n🔍 TEST 2: Alarm Timer Function")
    print("-" * 35)
    
    try:
        # Import required modules
        from app import alarm_timer
        
        # Set up global variables for testing
        import app
        app.timer_active = True
        app.door_open = True
        app.alarm_active = False
        
        # Test with 3 seconds for quick testing
        test_duration = 3
        print(f"Testing {test_duration} second timer...")
        
        start_time = time.time()
        alarm_timer(test_duration)
        end_time = time.time()
        
        actual_duration = end_time - start_time
        print(f"Expected: {test_duration}s, Actual: {actual_duration:.2f}s")
        
        if abs(actual_duration - test_duration) < 0.5:
            print("✅ Timer function working correctly")
            return True
        else:
            print("❌ Timer function has timing issues")
            return False
            
    except Exception as e:
        print(f"❌ Timer test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_audio_system():
    """Test 3: Audio system functionality"""
    print("\n🔍 TEST 3: Audio System")
    print("-" * 25)
    
    try:
        from app import initialize_audio, AUDIO_PATH
        
        print(f"Audio path: {AUDIO_PATH}")
        
        if AUDIO_PATH.exists():
            print("✅ Audio file found")
            
            # Test audio initialization
            if initialize_audio():
                print("✅ Audio system initialized successfully")
                return True
            else:
                print("❌ Audio initialization failed")
                return False
        else:
            print("⚠️ Audio file missing - place audio.mp3 in static/ directory")
            return False
            
    except Exception as e:
        print(f"❌ Audio test error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 eDOMOS-v2.1 COMPREHENSIVE TEST")
    print("=" * 50)
    
    # Test 1: Database Settings
    timer_duration = test_database_settings()
    
    # Test 2: Timer Function
    timer_works = test_timer_function()
    
    # Test 3: Audio System
    audio_works = test_audio_system()
    
    # Summary
    print("\n📊 TEST SUMMARY")
    print("=" * 20)
    print(f"Database Settings: {'✅' if timer_duration else '❌'}")
    print(f"Timer Function: {'✅' if timer_works else '❌'}")
    print(f"Audio System: {'✅' if audio_works else '❌'}")
    
    if timer_duration and timer_works and audio_works:
        print("\n🎉 All tests passed! System should work correctly.")
    else:
        print("\n⚠️ Some tests failed. Check the issues above.")

if __name__ == "__main__":
    main()
