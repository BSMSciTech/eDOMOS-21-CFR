#!/usr/bin/env python3
"""
Quick audio test with the new initialization settings
"""
import os
import sys
import time
import pygame

def test_audio_with_new_settings():
    """Test audio with the updated settings"""
    print("🔊 TESTING UPDATED AUDIO SETTINGS")
    print("=" * 40)
    
    try:
        # Apply the same settings as in the app
        os.environ['SDL_AUDIODRIVER'] = 'alsa'
        
        # Quit any existing mixer
        if pygame.mixer.get_init():
            pygame.mixer.quit()
            
        # Initialize with new settings
        pygame.mixer.pre_init(
            frequency=22050,
            size=-16, 
            channels=2, 
            buffer=512
        )
        pygame.mixer.init()
        
        print(f"✅ Mixer initialized: {pygame.mixer.get_init()}")
        print(f"🔧 SDL Audio Driver: {os.environ.get('SDL_AUDIODRIVER')}")
        
        # Load and test audio file
        audio_path = "static/audio.mp3"
        if os.path.exists(audio_path):
            pygame.mixer.music.load(audio_path)
            pygame.mixer.music.set_volume(0.8)
            
            print("🎵 Playing audio for 2 seconds...")
            pygame.mixer.music.play()
            
            start_time = time.time()
            while pygame.mixer.music.get_busy() and (time.time() - start_time) < 2:
                time.sleep(0.1)
                
            pygame.mixer.music.stop()
            print("✅ Audio test completed successfully")
            return True
        else:
            print("❌ Audio file not found")
            return False
            
    except Exception as e:
        print(f"❌ Audio test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_audio_with_new_settings()
