# ABOUTME: Test script to verify both TTS engines work correctly
# ABOUTME: Tests pyttsx3 and gTTS engines with fallback behavior

import os
import sys
from datetime import datetime

def test_engine(engine_name):
    """Test a specific TTS engine"""
    print(f"\n{'='*50}")
    print(f"Testing {engine_name.upper()} engine")
    print(f"{'='*50}")
    
    # Set environment variable
    os.environ["TTS_ENGINE"] = engine_name
    
    # Clear any existing imports to force re-initialization
    if 'main' in sys.modules:
        del sys.modules['main']
    
    try:
        import main
        
        print(f"Requested engine: {engine_name}")
        print(f"Actual engine: {main.TTS_ENGINE}")
        print(f"gTTS Available: {main.GTTS_AVAILABLE}")
        print(f"ElevenLabs Available: {main.ELEVENLABS_AVAILABLE}")
        print(f"ElevenLabs API Key: {'Set' if main.ELEVENLABS_API_KEY else 'Not set'}")
        print(f"TTS Engine Type: {type(main.tts_engine)}")
        
        # Check if the actual engine matches the requested engine
        if main.TTS_ENGINE != engine_name:
            print(f"✗ FAILED: Requested {engine_name} but got {main.TTS_ENGINE} (fallback occurred)")
            return False
        
        print(f"✓ Engine correctly initialized: {main.TTS_ENGINE}")
        
        # Test the speak function with a dynamic message including engine and time
        current_time = datetime.now().strftime("%H:%M:%S")
        test_message = f"Testing {engine_name} engine at {current_time}"
        result = main.speak(test_message, emotion="friendly")
        print(f"✓ Speak test result: {result}")
        
        # Verify the result contains the correct engine name
        if engine_name == "pyttsx3" and "engine: pyttsx3" not in result:
            print(f"✗ FAILED: Expected pyttsx3 in result but got: {result}")
            return False
        elif engine_name == "gtts" and "engine: gTTS" not in result:
            print(f"✗ FAILED: Expected gTTS in result but got: {result}")
            return False
        elif engine_name == "elevenlabs" and "engine: ElevenLabs" not in result:
            print(f"✗ FAILED: Expected ElevenLabs in result but got: {result}")
            return False
        
        # Test list_voices function
        voices_info = main.list_voices()
        print(f"✓ List voices: {len(voices_info)} characters returned")
        
        print(f"✓ {engine_name.upper()} engine working correctly")
        return True
        
    except Exception as e:
        print(f"✗ Error testing {engine_name}: {e}")
        return False

def main():
    """Test all engines"""
    print("TTS Engine Testing Script")
    print("This script tests pyttsx3, gTTS, and ElevenLabs engines")
    
    # Test pyttsx3 (should always work)
    success_pyttsx3 = test_engine("pyttsx3")
    
    # Test gTTS (depends on optional dependencies)
    success_gtts = test_engine("gtts")
    
    # Test ElevenLabs (depends on optional dependencies and API key)
    success_elevenlabs = test_engine("elevenlabs")
    
    print(f"\n{'='*50}")
    print("TEST SUMMARY")
    print(f"{'='*50}")
    print(f"pyttsx3 engine: {'✓ PASSED' if success_pyttsx3 else '✗ FAILED'}")
    print(f"gTTS engine: {'✓ PASSED' if success_gtts else '✗ FAILED'}")
    print(f"ElevenLabs engine: {'✓ PASSED' if success_elevenlabs else '✗ FAILED'}")
    
    if success_pyttsx3 and success_gtts and success_elevenlabs:
        print("\n🎉 All engines working correctly!")
    elif success_pyttsx3:
        print("\n⚠️  pyttsx3 working, other engines may need optional dependencies/API keys")
    else:
        print("\n❌ Issues detected with TTS engines")

if __name__ == "__main__":
    main()