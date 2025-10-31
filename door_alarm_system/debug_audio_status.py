#!/usr/bin/env python3
"""
Debug audio system status in the running app
"""
import os
import sys
sys.path.insert(0, '/home/bsm/WebApp/eDOMOS-v2/eDOMOS-v2.1/door_alarm_system')

# Set testing mode to avoid GPIO operations
os.environ['TESTING'] = '1'

def check_audio_status():
    """Check the current audio system status"""
    print("🔊 AUDIO SYSTEM STATUS CHECK")
    print("=" * 40)
    
    try:
        # Import the app modules
        from app import initialize_audio, audio_system_ready, AUDIO_PATH, alarm_volume
        import pygame
        
        print(f"📂 Audio file path: {AUDIO_PATH}")
        print(f"📁 File exists: {AUDIO_PATH.exists()}")
        
        if AUDIO_PATH.exists():
            file_size = AUDIO_PATH.stat().st_size
            print(f"📊 File size: {file_size} bytes")
        
        print(f"🎛️  Current alarm volume: {alarm_volume}")
        print(f"🔧 Audio system ready: {audio_system_ready}")
        print(f"🎮 Pygame mixer status: {pygame.mixer.get_init()}")
        
        # Test initialization
        print("\n🔧 Testing audio initialization...")
        result = initialize_audio()
        print(f"✅ Initialization result: {result}")
        
        # Check global variable after init
        from app import audio_system_ready
        print(f"🔧 Audio system ready after init: {audio_system_ready}")
        
    except Exception as e:
        print(f"❌ Error checking audio status: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_audio_status()
