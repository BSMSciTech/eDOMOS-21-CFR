#!/usr/bin/env python3
"""
Quick Audio Test - Test the audio alarm system for delay issues
"""
import pygame
import time
import os
from pathlib import Path

# Initialize pygame mixer
pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
pygame.mixer.init()

# Audio path
AUDIO_PATH = Path(__file__).parent / "static" / "audio.mp3"

print("🔊 Audio Delay Test")
print("=" * 40)
print(f"Audio file: {AUDIO_PATH}")
print(f"File exists: {AUDIO_PATH.exists()}")

if not AUDIO_PATH.exists():
    print("❌ Audio file not found!")
    exit(1)

# Test 1: Load as music (current method)
print("\n📍 Test 1: Music playback method")
start_time = time.time()
pygame.mixer.music.load(str(AUDIO_PATH))
pygame.mixer.music.set_volume(1.0)
print(f"Load time: {(time.time() - start_time) * 1000:.1f}ms")

start_time = time.time()
pygame.mixer.music.play()
print(f"Play command time: {(time.time() - start_time) * 1000:.1f}ms")
print("🎵 Playing... (press Enter to stop)")
input()
pygame.mixer.music.stop()

# Test 2: Try to load as Sound object (preloaded method)
print("\n📍 Test 2: Preloaded Sound object method")
try:
    start_time = time.time()
    sound = pygame.mixer.Sound(str(AUDIO_PATH))
    load_time = (time.time() - start_time) * 1000
    print(f"Load time: {load_time:.1f}ms")
    
    sound.set_volume(1.0)
    start_time = time.time()
    channel = sound.play(loops=-1)
    play_time = (time.time() - start_time) * 1000
    print(f"Play command time: {play_time:.1f}ms")
    print("🎵 Playing preloaded sound... (press Enter to stop)")
    input()
    channel.stop()
    
except Exception as e:
    print(f"❌ Sound object failed: {e}")
    print("💡 MP3 might not be supported for Sound objects, only Music")

print("\n✅ Test completed!")
print("Summary:")
print("- Music method: Works for MP3 but may have slight delay")
print("- Sound method: Would be instant but may not support MP3")
print("- Recommendation: Keep current music method with optimized settings")