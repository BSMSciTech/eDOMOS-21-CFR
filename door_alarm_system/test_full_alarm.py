#!/usr/bin/env python3
import os
import sys
import time
import threading
import pygame
import RPi.GPIO as GPIO
from pathlib import Path

# Configure paths
BASE_DIR = Path(__file__).parent.resolve()
AUDIO_PATH = BASE_DIR / "static/audio.mp3"

# GPIO Configuration
DOOR_SENSOR_PIN = 18
WHITE_LED_PIN = 24
RED_LED_PIN = 23

# Global variables
door_open = False
alarm_active = False
timer_active = False
audio_system_ready = False
alarm_volume = 0.8

def init_gpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(DOOR_SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(WHITE_LED_PIN, GPIO.OUT)
    GPIO.setup(RED_LED_PIN, GPIO.OUT)
    GPIO.output(WHITE_LED_PIN, GPIO.LOW)
    GPIO.output(RED_LED_PIN, GPIO.LOW)
    print("✅ GPIO initialized")

def initialize_audio():
    global audio_system_ready
    
    try:
        print("🔊 Initializing audio system...")
        os.environ['SDL_AUDIODRIVER'] = 'alsa'
        os.environ['ALSA_PCM_DEVICE'] = '0'
        
        if pygame.mixer.get_init():
            pygame.mixer.quit()
        
        pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
        pygame.mixer.init()
        
        if AUDIO_PATH.exists():
            pygame.mixer.music.load(str(AUDIO_PATH))
            pygame.mixer.music.set_volume(alarm_volume)
            audio_system_ready = True
            print(f"✅ Audio system ready")
        else:
            print(f"❌ Audio file not found")
            audio_system_ready = False
            
        return audio_system_ready
        
    except Exception as e:
        print(f"❌ Audio initialization failed: {e}")
        audio_system_ready = False
        return False

def play_alarm():
    global alarm_active, audio_system_ready
    
    print("🚨 Starting alarm sound...")
    
    if not audio_system_ready:
        initialize_audio()
    
    try:
        while alarm_active:
            if not alarm_active:
                break
                
            print("🎵 Playing alarm...")
            pygame.mixer.music.play()
            
            while pygame.mixer.music.get_busy() and alarm_active:
                time.sleep(0.1)
                
            if alarm_active:
                time.sleep(0.1)
                
    except Exception as e:
        print(f"❌ Alarm playback error: {e}")

def test_alarm_system():
    global alarm_active
    
    print("=" * 50)
    print("🚪 DOOR ALARM SYSTEM TEST")
    print("=" * 50)
    
    init_gpio()
    initialize_audio()
    
    print("\n🚨 Testing alarm for 5 seconds...")
    alarm_active = True
    
    alarm_thread = threading.Thread(target=play_alarm, daemon=True)
    alarm_thread.start()
    
    time.sleep(5)
    
    alarm_active = False
    pygame.mixer.music.stop()
    
    print("\n✅ Test completed!")
    
    GPIO.cleanup()

if __name__ == "__main__":
    try:
        test_alarm_system()
    except KeyboardInterrupt:
        print("\n⏹️ Test interrupted")
    except Exception as e:
        print(f"\n❌ Test error: {e}")
