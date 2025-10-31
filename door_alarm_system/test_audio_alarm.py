#!/usr/bin/env python3
"""Test script for audio alarm functionality"""

import pygame
from pathlib import Path

def test_audio():
    base_dir = Path('/home/bsm/WebApp/eDOMOS-v2/eDOMOS-v2.1/door_alarm_system')
    audio_path = base_dir / "static" / "audio.mp3"
    
    print("Testing audio setup...")
    print(f"Audio path: {audio_path}")
    
    if audio_path.exists():
        print("✅ Audio file found")
        try:
            pygame.mixer.init()
            pygame.mixer.music.load(str(audio_path))
            print("✅ Audio system ready")
        except Exception as e:
            print(f"❌ Audio error: {e}")
    else:
        print("⚠️ Audio file missing - place audio.mp3 in static/ directory")

if __name__ == "__main__":
    test_audio()
