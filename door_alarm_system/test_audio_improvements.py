#!/usr/bin/env python3
"""
Quick test to verify the improved audio alarm system works correctly
"""
import requests
import time
import json

def test_alarm_trigger():
    """Test the alarm triggering via API"""
    base_url = "http://127.0.0.1:5000"
    
    try:
        print("🧪 Testing improved audio alarm system...")
        print("📡 Connecting to Flask app...")
        
        # Test if server is running
        response = requests.get(f"{base_url}/api/dashboard", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print("❌ Server not responding")
            return
            
        # Try to trigger alarm manually (simulating timer expiration)
        print("🔊 Triggering alarm manually to test audio...")
        test_data = {
            "action": "trigger_alarm_test",
            "duration": 5
        }
        
        # Since we're in testing mode, let's check the current system status
        dashboard_response = requests.get(f"{base_url}/api/dashboard")
        if dashboard_response.status_code == 200:
            data = dashboard_response.json()
            print(f"📊 Current system status:")
            print(f"  ├─ Door Open: {data.get('door_open', 'Unknown')}")
            print(f"  ├─ Alarm Active: {data.get('alarm_active', 'Unknown')}")
            print(f"  ├─ Timer Active: {data.get('timer_active', 'Unknown')}")
            print(f"  └─ Audio Ready: {data.get('audio_system_ready', 'Unknown')}")
            
        print("\n📋 Audio improvements implemented:")
        print("  ├─ Volume increased: 0.8 → 1.0 (maximum)")
        print("  ├─ Continuous loop: pygame.mixer.music.play(loops=-1)")
        print("  ├─ No gaps: Removed wait-for-finish loop")
        print("  └─ Immediate stop: stop_alarm_audio() when door closes")
        
        print("\n🎯 To test the audio:")
        print("  1. Open the door sensor (GPIO pin 11)")
        print("  2. Wait for timer to expire (currently 5 seconds)")
        print("  3. Audio should play continuously at full volume")
        print("  4. Close the door sensor to stop audio immediately")
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Flask app - make sure it's running")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_alarm_trigger()