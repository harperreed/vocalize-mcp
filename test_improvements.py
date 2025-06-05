# ABOUTME: Tests for the improved voice functionality addressing issues.md
# ABOUTME: Tests validation, thread safety, caching, logging, and platform compatibility
import pytest
from unittest.mock import Mock, patch, MagicMock
import threading
import time
import main


class TestVoiceImprovements:
    """Test improvements made to address issues in issues.md"""
    
    def test_input_validation_empty_text(self):
        """Test validation of empty text input"""
        result = main.speak("")
        assert "❌ Error: Text cannot be empty" in result
        
        result = main.speak("   ")  # Whitespace only
        assert "❌ Error: Text cannot be empty" in result
    
    def test_input_validation_rate_bounds(self):
        """Test validation of rate parameter bounds"""
        # Test too low
        result = main.speak("Hello", rate=30)
        assert "Rate must be between 50 and 400" in result
        
        # Test too high
        result = main.speak("Hello", rate=500)
        assert "Rate must be between 50 and 400" in result
        
        # Test valid bounds
        result = main.speak("Hello", rate=50)
        assert "🗣️ Spoke:" in result
        
        result = main.speak("Hello", rate=400)
        assert "🗣️ Spoke:" in result
    
    def test_input_validation_rate_type(self):
        """Test validation of rate parameter type"""
        result = main.speak("Hello", rate="invalid")
        assert "Rate must be a number" in result
    
    def test_configurable_rate_calculations(self):
        """Test that rate calculations use configurable multipliers"""
        # Test each emotion multiplier
        emotions_to_test = [
            ("dramatic", 1.2),
            ("cheerful", 1.13),
            ("playful", 1.07),
            ("professional", 1.0),
            ("calm", 0.87),
            ("friendly", 1.0)
        ]
        
        base_rate = 100
        for emotion, expected_multiplier in emotions_to_test:
            calculated_rate = main.calculate_emotion_rate(base_rate, emotion)
            expected_rate = int(base_rate * expected_multiplier)
            assert calculated_rate == expected_rate, f"Emotion {emotion}: expected {expected_rate}, got {calculated_rate}"
    
    def test_platform_specific_voice_emotions(self):
        """Test that voice emotions are platform-specific"""
        # Test that the function returns different configs for different platforms
        with patch('platform.system', return_value='Darwin'):
            macos_config = main.get_voice_emotions_for_platform()
            
        with patch('platform.system', return_value='Windows'):
            windows_config = main.get_voice_emotions_for_platform()
            
        with patch('platform.system', return_value='Linux'):
            linux_config = main.get_voice_emotions_for_platform()
        
        # They should have different voice lists
        assert macos_config != windows_config
        assert macos_config != linux_config
        assert windows_config != linux_config
        
        # But same emotion categories
        assert set(macos_config.keys()) == set(windows_config.keys()) == set(linux_config.keys())
    
    def test_voice_cache_efficiency(self):
        """Test that voice cache improves lookup efficiency"""
        # This tests that the cache is actually being used
        assert isinstance(main._voice_cache, dict)
        
        # If voices are available, cache should be populated
        if main._available_voices:
            assert len(main._voice_cache) > 0
            
            # Test that find_voice_by_emotion_and_name uses cache
            voice_index = main.find_voice_by_emotion_and_name(voice_name="albert")
            assert isinstance(voice_index, int)
            assert voice_index >= 0
    
    def test_error_handling_no_tts_engine(self):
        """Test graceful handling when TTS engine is not available"""
        # Temporarily disable TTS engine
        original_engine = main.tts_engine
        main.tts_engine = None
        
        try:
            result = main.speak("Hello")
            assert "❌ Error: Text-to-speech engine not available" in result
        finally:
            # Restore original engine
            main.tts_engine = original_engine
    
    @patch('main.tts_engine')
    def test_thread_safety_concurrent_speak(self, mock_engine):
        """Test that concurrent speak operations are thread-safe using mocked engine"""
        # Mock the TTS engine to avoid actual audio playback conflicts
        mock_voices = [Mock()]
        mock_voices[0].name = "Test Voice"
        mock_voices[0].id = "test.voice"
        mock_engine.getProperty.return_value = mock_voices
        
        results = []
        errors = []
        
        def speak_worker(text, index):
            try:
                result = main.speak(f"Test {index}", emotion="friendly")
                results.append(result)
            except Exception as e:
                errors.append(str(e))
        
        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=speak_worker, args=(f"Test {i}", i))
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check results
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(results) == 5, f"Expected 5 results, got {len(results)}"
        
        # All should be successful
        for result in results:
            assert "🗣️ Spoke:" in result
        
        # Verify that the mock engine was called the expected number of times
        assert mock_engine.say.call_count == 5
        assert mock_engine.runAndWait.call_count == 5
    
    def test_logging_functionality(self):
        """Test that logging is working properly"""
        import logging
        
        # Check that logger exists
        assert hasattr(main, 'logger')
        assert isinstance(main.logger, logging.Logger)
        
        # Test that log messages are generated during speak operation
        with patch.object(main.logger, 'info') as mock_info:
            main.speak("Test logging", emotion="friendly")
            
            # Should have logged the speak operation
            assert mock_info.called
            
            # Check that log message contains expected information
            log_calls = [call.args[0] for call in mock_info.call_args_list]
            speak_logged = any("Speaking text:" in msg for msg in log_calls)
            assert speak_logged, f"Expected speaking log message not found in: {log_calls}"
    
    def test_cleanup_mechanism(self):
        """Test that cleanup mechanism is registered"""
        import atexit
        
        # Check that cleanup function is registered
        # Note: This is a basic test - actual cleanup testing would require
        # more complex mocking of the atexit module
        assert hasattr(main, 'cleanup_tts_engine')
        assert callable(main.cleanup_tts_engine)
    
    def test_available_voices_validation(self):
        """Test that voice emotions are updated with actually available voices"""
        if main._available_voices:
            # Check that emotion categories have been updated with available voices
            for emotion, config in main.VOICE_EMOTIONS.items():
                assert "available_voices" in config or "voices" in config
                
                # Available voices should be a list
                available = config.get("available_voices", config.get("voices", []))
                assert isinstance(available, list)
                assert len(available) > 0


class TestErrorRecovery:
    """Test error recovery and fallback mechanisms"""
    
    @patch('main.tts_engine')
    def test_speak_with_tts_exception(self, mock_engine):
        """Test graceful handling of TTS engine exceptions"""
        # Mock TTS engine to raise exception
        mock_engine.say.side_effect = Exception("TTS engine error")
        
        result = main.speak("Test error handling")
        
        assert "❌ Error speaking text: TTS engine error" in result
    
    def test_voice_finding_fallback(self):
        """Test fallback when requested voice is not found"""
        # Test with non-existent voice
        voice_index = main.find_voice_by_emotion_and_name(voice_name="NonExistentVoice")
        assert voice_index == 0  # Should fallback to first voice
        
        # Test with non-existent emotion
        voice_index = main.find_voice_by_emotion_and_name(emotion="nonexistent")
        assert voice_index == 0  # Should fallback to first voice


if __name__ == "__main__":
    pytest.main([__file__, "-v"])