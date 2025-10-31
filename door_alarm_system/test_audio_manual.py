#!/usr/bin/env python3
"""
Manual audio test for debugging
"""
import os
import sys
import time
import pygame
from pathlib import Path

def test_audio_playback():
    """Test audio playback manually"""
    
    print("🔊 MANUAL AUDIO TEST")
    print("=" * 30)
    
    # Set up audio path
    base_dir = Path('/home/bsm/WebApp/eDOMOS-v2/eDOMOS-v2.1/door_alarm_system')
    audio_path = base_dir / "static" / "audio.mp3"
    
    print(f"Audio path: {audio_path}")
    print(f"File exists: {audio_path.exists()}")
    
    if not audio_path.exists():
        print("❌ Audio file not found")
        return False
    
    file_size = audio_path.stat().st_size
    print(f"File size: {file_size} bytes")
    
    try:
        # Initialize pygame mixer
        print("\n🔧 Initializing pygame mixer...")
        pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=1024)
        pygame.mixer.init()
        
        print(f"Mixer initialized: {pygame.mixer.get_init()}")
        
        # Load audio file
        print("📂 Loading audio file...")
        pygame.mixer.music.load(str(audio_path))
        pygame.mixer.music.set_volume(0.8)
        
        print("✅ Audio loaded successfully")
        
        # Test playback
        print("\n🎵 Playing audio for 3 seconds...")
        pygame.mixer.music.play()
        
        start_time = time.time()
        while pygame.mixer.music.get_busy() and (time.time() - start_time) < 3:
            time.sleep(0.1)
            
        pygame.mixer.music.stop()
        print("🔇 Audio test completed")
        
        return True
        
    except Exception as e:
        print(f"❌ Audio test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_audio_playback()
