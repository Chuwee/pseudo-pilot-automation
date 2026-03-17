#!/usr/bin/env python3
"""
Test script for Piper TTS voice playback
"""

from src.piem.interfaces.voice_playback import VoicePlayback

def main():
    print("Initializing voice playback system...")
    voice = VoicePlayback()
    
    print("Testing voice synthesis and playback...")
    test_message = "Roger that, Iberia five five nine, climb and maintain flight level two five zero."
    
    print(f"Playing: {test_message}")
    voice.play(test_message)
    
    print("Playback complete!")

if __name__ == "__main__":
    main()
