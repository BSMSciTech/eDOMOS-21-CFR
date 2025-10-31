#!/usr/bin/env python3
import os
import sys
import time
import pygame
from pathlib import Path

def test_audio_system():
    print("=" * 60)
    print("COMPLETE AUDIO SYSTEM TEST")
    print("=" * 60)
    
    # Test 1: Check audio file
    print("\n1. AUDIO FILE CHECK:")
    audio_path = Path("static/audio.mp3")
    print(f"   File path: {audio_path}")
    print(f"   File exists: {audio_path.exists()}")
    
    if audio_path.exists():
        file_size = audio_path.stat().st_size
        print(f"   File size: {file_size} bytes")
    else:
        print("   ERROR: Audio file not found!")
        return False
    
    # Test 2: Set SDL audio driver
    print("\n2. SDL CONFIGURATION:")
    os.environ['SDL_AUDIODRIVER'] = 'alsa'
    print(f"   SDL_AUDIODRIVER: {os.environ.get('SDL_AUDIODRIVER')}")
    
    # Test 3: Initialize pygame
    print("\n3. PYGAME INITIALIZATION:")
    try:
        if pygame.mixer.get_init():
            pygame.mixer.quit()
            print("   Existing mixer quit")
        
        pygame.mixer.pre_init(
            frequency=22050,
            size=-16,
            channels=2,
            buffer=512
        )
        pygame.mixer.init()
        
        init_status = pygame.mixer.get_init()
        print(f"   Mixer initialized: {init_status}")
        
        if not init_status:
            print("   ERROR: Pygame mixer failed to initialize!")
            return False
            
    except Exception as e:
        print(f"   ERROR: Pygame initialization error: {e}")
        return False
    
    # Test 4: Load audio file
    print("\n4. AUDIO FILE LOADING:")
    try:
        pygame.mixer.music.load(str(audio_path))
        print("   SUCCESS: Audio file loaded")
    except Exception as e:
        print(f"   ERROR: Audio loading error: {e}")
        return False
    
    # Test 5: Audio playback test
    print("\n5. AUDIO PLAYBACK TEST:")
    print("   Starting 3-second audio test...")
    
    try:
        pygame.mixer.music.set_volume(0.8)
        pygame.mixer.music.play()
        print("   Audio playback started...")
        
        start_time = time.time()
        test_duration = 3.0
        
        while time.time() - start_time < test_duration:
            if not pygame.mixer.music.get_busy():
                print("   Audio finished playing")
                break
            time.sleep(0.1)
        
        pygame.mixer.music.stop()
        print("   Audio test completed")
        
    except Exception as e:
        print(f"   ERROR: Audio playback error: {e}")
        return False
    
    print("\nSUCCESS: AUDIO SYSTEM TEST COMPLETED")
    print("If you heard audio, the system is working!")
    return True

if __name__ == "__main__":
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    print("Testing audio system for eDOMOS-v2 door alarm...")
    test_audio_system()