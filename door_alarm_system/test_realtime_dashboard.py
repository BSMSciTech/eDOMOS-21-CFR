#!/usr/bin/env python3
"""
Comprehensive test of the real-time dashboard system
"""

import sys
import os
import time
sys.path.append(os.path.dirname(__file__))

from app import app, log_event

def test_realtime_dashboard():
    print("🚀 TESTING REAL-TIME DASHBOARD UPDATES")
    print("=" * 50)
    
    with app.app_context():
        # Test 1: Door Events
        print("\n📊 Test 1: Door Opening")
        log_event('door_open', 'Dashboard test: Door opened')
        print("✅ Door open event sent to dashboard")
        
        time.sleep(2)
        
        print("\n📊 Test 2: Door Closing")  
        log_event('door_close', 'Dashboard test: Door closed')
        print("✅ Door close event sent to dashboard")
        
        time.sleep(2)
        
        print("\n📊 Test 3: Alarm Trigger")
        log_event('alarm_triggered', 'Dashboard test: Alarm activated')
        print("✅ Alarm event sent to dashboard")
        
    print("\n🎯 TEST COMPLETED")
    print("Dashboard should show real-time updates for:")
    print("  - Door Status")
    print("  - Alarm Status") 
    print("  - Total Events Counter")
    print("  - Event Statistics")

if __name__ == '__main__':
    test_realtime_dashboard()
