# ABOUTME: Integration tests for the complete vocalize MCP server functionality
# ABOUTME: Tests real voice operations without mocking for end-to-end validation
import pytest
import main


class TestRealVoiceIntegration:
    """Integration tests using real TTS engine (no mocking)"""
    
    def test_real_voice_listing(self):
        """Test that we can actually list real voices"""
        result = main.list_voices()
        
        # Should contain expected content
        assert "🎯 RECOMMENDED EMOTIONS:" in result
        assert "voices available on your system" in result
    
    def test_real_emotion_listing(self):
        """Test that emotion listing works with real data"""
        result = main.list_emotions()
        
        assert "🎭 EMOTION CATEGORIES FOR EXPRESSIVE SPEECH:" in result
        assert "CHEERFUL" in result
        assert "DRAMATIC" in result
        assert "💡 USAGE EXAMPLES:" in result
    
    def test_real_voice_guide(self):
        """Test that voice guide provides complete information"""
        result = main.voice_guide()
        
        # Check all major sections are present
        sections = [
            "🎙️ VOCALIZE AGENT",
            "🎯 PURPOSE:",
            "🗣️ MAIN FUNCTION:",
            "📋 EMOTION CATEGORIES & WHEN TO USE:",
            "💡 BEST PRACTICES FOR AI AGENTS:",
            "🔧 DISCOVERY TOOLS:",
            "🎯 QUICK REFERENCE:"
        ]
        
        for section in sections:
            assert section in result
    
    def test_emotion_voice_mapping(self):
        """Test that all emotions have valid voice mappings"""
        # This tests the real voice finding logic
        for emotion in main.VOICE_EMOTIONS.keys():
            # Should not raise exception and should return valid index
            voice_index = main.find_voice_by_emotion_and_name(emotion=emotion)
            assert isinstance(voice_index, int)
            assert voice_index >= 0
    
    def test_specific_voice_finding(self):
        """Test finding specific voices that should exist on macOS"""
        common_voices = ["albert", "fred", "good", "bad"]
        
        for voice_name in common_voices:
            voice_index = main.find_voice_by_emotion_and_name(voice_name=voice_name)
            assert isinstance(voice_index, int)
            assert voice_index >= 0
    
    @pytest.mark.slow
    def test_actual_speech(self):
        """Test actual speech generation (marked as slow test)"""
        # Note: This will actually play audio if run
        # Use with caution in automated testing environments
        
        result = main.speak("Test message", emotion="friendly")
        
        # Should return success message
        assert "🗣️ Spoke:" in result
        assert "Test message" in result
        assert "emotion: friendly" in result
    
    def test_error_handling_with_invalid_emotion(self):
        """Test that invalid emotions don't break the system"""
        # Should not raise exception, should fall back gracefully
        result = main.speak("Test", emotion="nonexistent_emotion")
        
        # Should still work (fallback to default)
        assert "🗣️ Spoke:" in result or "Error" in result
    
    def test_all_tools_discoverable(self):
        """Test that all main tools are available and callable"""
        tools = [
            main.speak,
            main.list_voices,
            main.list_emotions,
            main.voice_guide
        ]
        
        for tool in tools:
            assert callable(tool)
            # Verify the function has proper docstring
            assert tool.__doc__ is not None
            assert len(tool.__doc__.strip()) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "not slow"])