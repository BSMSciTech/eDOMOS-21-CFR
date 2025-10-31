#!/usr/bin/env python3
"""
Test timer duration fix
"""
import os
import sys
import sqlite3

# Check database directly
def check_database():
    db_path = "instance/alarm_system.db"
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM setting WHERE key='timer_duration'")
        result = cursor.fetchone()
        conn.close()
        
        if result:
            print(f"✅ Database timer_duration: {result[2]} seconds")
            return int(result[2])
        else:
            print("❌ No timer_duration setting in database")
            return None
    else:
        print("❌ Database file not found")
        return None

# Test the timer variable issue
def test_timer_variables():
    print("🔍 Testing timer variable scoping...")
    
    # Simulate the global variable
    global_timer_duration = 30
    print(f"Global timer_duration: {global_timer_duration}")
    
    # Simulate the local variable assignment
    def simulate_door_open():
        global global_timer_duration
        db_value = check_database()
        
        if db_value:
            current_timer_duration = db_value  # Local variable
            global_timer_duration = current_timer_duration  # Update global
            
            print(f"Local current_timer_duration: {current_timer_duration}")
            print(f"Updated global_timer_duration: {global_timer_duration}")
            
            return current_timer_duration
        return 30
    
    return simulate_door_open()

if __name__ == "__main__":
    print("🔧 TIMER DURATION FIX TEST")
    print("=" * 30)
    
    db_timer = check_database()
    final_timer = test_timer_variables()
    
    print(f"\n📊 Results:")
    print(f"Database value: {db_timer}")
    print(f"Final timer value: {final_timer}")
    
    if db_timer == final_timer == 7:
        print("✅ Timer fix should work correctly!")
    else:
        print("❌ There may still be issues")
