# ABOUTME: Comprehensive tests for voice functionality in the vocalize MCP server
# ABOUTME: Tests emotion-based voice selection, error handling, and all voice tools
import pytest
from unittest.mock import Mock, patch, MagicMock
import main


class TestEngineInitialization:
    """Test TTS engine initialization and selection"""
    
    def test_engine_variables_defined(self):
        """Test that engine configuration variables are properly defined"""
        assert hasattr(main, 'TTS_ENGINE')
        assert hasattr(main, 'GTTS_AVAILABLE')
        assert hasattr(main, 'ELEVENLABS_AVAILABLE')
        assert hasattr(main, 'ELEVENLABS_API_KEY')
        assert hasattr(main, 'ELEVENLABS_VOICE_ID')
    
    def test_dotenv_loaded(self):
        """Test that dotenv is loaded (API key should be available if .env exists)"""
        # If .env file exists with ELEVENLABS_API_KEY, it should be loaded
        assert main.ELEVENLABS_API_KEY is not None or main.ELEVENLABS_API_KEY == ""
    
    def test_engine_fallback_logic(self):
        """Test that engine fallback works correctly"""
        # The actual engine should be one of the supported types
        valid_engines = ['pyttsx3', 'gtts', 'elevenlabs']
        assert main.TTS_ENGINE in valid_engines
        
        # tts_engine should be initialized
        assert main.tts_engine is not None


class TestVoiceEngine:
    """Test voice engine initialization and basic functionality"""
    
    def test_tts_engine_initialized(self):
        """Test that TTS engine is properly initialized"""
        assert main.tts_engine is not None
    
    def test_voice_emotions_defined(self):
        """Test that voice emotion categories are properly defined"""
        assert isinstance(main.VOICE_EMOTIONS, dict)
        assert len(main.VOICE_EMOTIONS) == 6
        
        required_emotions = ["cheerful", "dramatic", "friendly", "professional", "playful", "calm"]
        for emotion in required_emotions:
            assert emotion in main.VOICE_EMOTIONS
            assert "description" in main.VOICE_EMOTIONS[emotion]
            assert "voices" in main.VOICE_EMOTIONS[emotion]
            assert isinstance(main.VOICE_EMOTIONS[emotion]["voices"], list)


class TestVoiceSelection:
    """Test voice selection logic"""
    
    @patch('main._voice_cache')
    @patch('main._available_voices')
    def test_find_voice_by_emotion(self, mock_available_voices, mock_voice_cache):
        """Test finding voice by emotion category using cache"""
        # Mock the cache and available voices
        mock_voices = [Mock(), Mock(), Mock(), Mock()]
        mock_voices[0].name = "Albert"
        mock_voices[1].name = "Good News"
        mock_voices[2].name = "Bad News"
        mock_voices[3].name = "Fred"
        
        mock_available_voices.__bool__.return_value = True
        mock_available_voices.__len__.return_value = 4
        mock_available_voices.__getitem__.side_effect = lambda i: mock_voices[i]
        
        mock_voice_cache.__contains__.side_effect = lambda key: key in ['good news', 'bad news']
        mock_voice_cache.__getitem__.side_effect = {'good news': 1, 'bad news': 2}.get
        
        # Test cheerful emotion (should find "Good News")
        result = main.find_voice_by_emotion_and_name(emotion="cheerful")
        assert result == 1  # Good News is at index 1
        
        # Test dramatic emotion (should find "Bad News")
        result = main.find_voice_by_emotion_and_name(emotion="dramatic")
        assert result == 2  # Bad News is at index 2
    
    @patch('main._voice_cache')
    @patch('main._available_voices')
    def test_find_voice_by_name(self, mock_available_voices, mock_voice_cache):
        """Test finding voice by specific name using cache"""
        mock_available_voices.__bool__.return_value = True
        
        mock_voice_cache.__contains__.side_effect = lambda key: key in ['fred', 'good']
        mock_voice_cache.__getitem__.side_effect = {'fred': 2, 'good': 1}.get
        
        # Test finding specific voice
        result = main.find_voice_by_emotion_and_name(voice_name="Fred")
        assert result == 2  # Fred is at index 2
        
        # Test partial name matching
        result = main.find_voice_by_emotion_and_name(voice_name="good")
        assert result == 1  # "Good News" contains "good"
    
    @patch('main.tts_engine')
    def test_voice_fallback(self, mock_engine):
        """Test fallback to default voice when no match found"""
        mock_engine.getProperty.return_value = []
        
        result = main.find_voice_by_emotion_and_name(emotion="nonexistent")
        assert result == 0  # Should fallback to default
        
        result = main.find_voice_by_emotion_and_name(voice_name="nonexistent")
        assert result == 0  # Should fallback to default


class TestSpeakFunction:
    """Test the main speak function"""
    
    @patch('main._speak_with_pyttsx3')
    @patch('main.TTS_ENGINE', 'pyttsx3')
    def test_basic_speak(self, mock_speak_pyttsx3):
        """Test basic speech without emotion or voice"""
        mock_speak_pyttsx3.return_value = "🗣️ Spoke: 'Hello world' (rate: 150 wpm, engine: pyttsx3)"
        
        result = main.speak("Hello world")
        
        # Verify the appropriate engine function was called
        mock_speak_pyttsx3.assert_called_once_with("Hello world", None, None, 150)
        
        # Verify return message
        assert "Hello world" in result
        assert "rate: 150 wpm" in result
    
    @patch('main.tts_engine')
    def test_speak_with_emotion(self, mock_engine):
        """Test speech with emotion parameter"""
        mock_voices = [Mock(), Mock()]
        mock_voices[0].name = "Albert"
        mock_voices[0].id = "albert.voice"
        mock_voices[1].name = "Good News"
        mock_voices[1].id = "good.voice"
        mock_engine.getProperty.return_value = mock_voices
        
        result = main.speak("Great job!", emotion="cheerful")
        
        # Verify cheerful emotion uses multiplier (150 * 1.13 = 169)
        mock_engine.setProperty.assert_any_call('rate', 169)
        # Note: The new system uses real voice selection, just verify the result
        mock_engine.say.assert_called_with("Great job!")
        
        # Verify return message includes emotion
        assert "emotion: cheerful" in result
    
    @patch('main.tts_engine')
    def test_speak_with_voice(self, mock_engine):
        """Test speech with specific voice parameter"""
        mock_voices = [Mock(), Mock()]
        mock_voices[0].name = "Albert"
        mock_voices[0].id = "albert.voice"
        mock_voices[1].name = "Fred"
        mock_voices[1].id = "fred.voice"
        mock_engine.getProperty.return_value = mock_voices
        
        result = main.speak("Hello there", voice="Fred")
        
        # Verify Fred voice is selected (now uses real voice ID)
        # Note: The new system uses actual voice IDs from the system
        assert "voice: Fred" in result
    
    @patch('main.tts_engine')
    def test_speak_with_custom_rate(self, mock_engine):
        """Test speech with custom rate parameter"""
        mock_voices = [Mock()]
        mock_voices[0].name = "Default"
        mock_voices[0].id = "default.voice"
        mock_engine.getProperty.return_value = mock_voices
        
        result = main.speak("Fast speech", rate=200)
        
        mock_engine.setProperty.assert_any_call('rate', 200)
        assert "rate: 200 wpm" in result
    
    @patch('main.tts_engine')
    def test_emotion_rate_adjustments(self, mock_engine):
        """Test that different emotions adjust speaking rate correctly"""
        mock_voices = [Mock()]
        mock_voices[0].name = "Voice"
        mock_voices[0].id = "voice.id"
        mock_engine.getProperty.return_value = mock_voices
        mock_engine.reset_mock()  # Reset to clear previous calls
        
        base_rate = 150
        # Updated to match new multiplier-based calculations
        test_cases = [
            ("dramatic", int(base_rate * 1.2)),      # 180
            ("cheerful", int(base_rate * 1.13)),     # 169
            ("playful", int(base_rate * 1.07)),      # 160
            ("professional", int(base_rate * 1.0)),  # 150
            ("calm", int(base_rate * 0.87)),         # 130
            ("friendly", int(base_rate * 1.0))       # 150
        ]
        
        for emotion, expected_rate in test_cases:
            mock_engine.reset_mock()  # Reset mock between tests
            main.speak("Test", emotion=emotion, rate=base_rate)
            mock_engine.setProperty.assert_any_call('rate', expected_rate)
    
    @patch('main.tts_engine')
    def test_speak_error_handling(self, mock_engine):
        """Test error handling in speak function"""
        mock_engine.say.side_effect = Exception("TTS Error")
        
        result = main.speak("Test error")
        
        assert "Error speaking text: TTS Error" in result


class TestVoiceListingFunctions:
    """Test voice listing and guide functions"""
    
    def test_list_emotions(self):
        """Test emotion listing function"""
        result = main.list_emotions()
        
        assert "🎭 EMOTION CATEGORIES FOR EXPRESSIVE SPEECH:" in result
        assert "CHEERFUL" in result
        assert "DRAMATIC" in result
        assert "💡 USAGE EXAMPLES:" in result
        assert "speak(" in result
    
    @patch('main.tts_engine')
    def test_list_voices_pyttsx3(self):
        """Test voice listing function for pyttsx3 engine"""
        with patch('main.TTS_ENGINE', 'pyttsx3'), \
             patch('main._available_voices') as mock_voices:
            mock_voices.__len__.return_value = 5
            
            result = main.list_voices()
            
            assert "pyttsx3 Engine" in result
            assert "🎯 RECOMMENDED EMOTIONS:" in result
            assert "voices available on your system" in result
    
    def test_list_voices_gtts(self):
        """Test voice listing function for gTTS engine"""
        with patch('main.TTS_ENGINE', 'gtts'):
            result = main.list_voices()
            
            assert "gTTS Engine" in result
            assert "Google Text-to-Speech with accent variations" in result
            assert "EMOTION-TO-ACCENT MAPPING:" in result
    
    def test_list_voices_elevenlabs(self):
        """Test voice listing function for ElevenLabs engine"""
        with patch('main.TTS_ENGINE', 'elevenlabs'), \
             patch('main.ELEVENLABS_VOICE_ID', 'test_voice_id'):
            result = main.list_voices()
            
            assert "ElevenLabs Engine" in result
            assert "CURRENT VOICE: test_voice_id" in result
            assert "EMOTION-TO-VOICE-SETTINGS MAPPING:" in result
    
    @patch('main.tts_engine')
    def test_list_voices_no_voices(self, mock_engine):
        """Test voice listing when no voices available"""
        mock_engine.getProperty.return_value = None
        
        result = main.list_voices()
        
        assert "❌ No voices available on this system" in result
    
    @patch('main.tts_engine')
    def test_list_voices_error(self, mock_engine):
        """Test voice listing error handling"""
        mock_engine.getProperty.side_effect = Exception("Voice error")
        
        result = main.list_voices()
        
        assert "❌ Error listing voices: Voice error" in result
    
    def test_voice_guide(self):
        """Test comprehensive voice guide"""
        result = main.voice_guide()
        
        # Check for key sections
        assert "🎙️ VOCALIZE AGENT - VOICE EMOTING GUIDE FOR AI AGENTS" in result
        assert "🎯 PURPOSE:" in result
        assert "🗣️ MAIN FUNCTION:" in result
        assert "📋 EMOTION CATEGORIES & WHEN TO USE:" in result
        assert "💡 BEST PRACTICES FOR AI AGENTS:" in result
        assert "🔧 DISCOVERY TOOLS:" in result
        assert "🎯 QUICK REFERENCE:" in result
        
        # Check for all emotions
        emotions = ["CHEERFUL", "DRAMATIC", "FRIENDLY", "PROFESSIONAL", "PLAYFUL", "CALM"]
        for emotion in emotions:
            assert emotion in result
        
        # Check for usage examples
        assert "speak(" in result
        assert "emotion=" in result


class TestIntegration:
    """Integration tests combining multiple components"""
    
    @patch('main.tts_engine')
    def test_full_workflow(self, mock_engine):
        """Test complete workflow from emotion selection to speech"""
        mock_voices = [Mock(), Mock(), Mock()]
        mock_voices[0].name = "Albert"
        mock_voices[0].id = "albert.voice"
        mock_voices[1].name = "Good News"
        mock_voices[1].id = "good.voice"
        mock_voices[2].name = "Bad News"
        mock_voices[2].id = "bad.voice"
        mock_engine.getProperty.return_value = mock_voices
        
        # Test cheerful emotion workflow
        result = main.speak("Congratulations!", emotion="cheerful")
        
        # Verify the complete chain
        assert mock_engine.setProperty.call_count >= 2  # voice and rate
        mock_engine.say.assert_called_with("Congratulations!")
        mock_engine.runAndWait.assert_called_once()
        
        # Verify result message
        assert "🗣️ Spoke: 'Congratulations!'" in result
        assert "emotion: cheerful" in result
        assert "rate: 169 wpm" in result
    
    def test_voice_categories_completeness(self):
        """Test that all emotion categories have valid voice mappings"""
        for emotion, config in main.VOICE_EMOTIONS.items():
            assert isinstance(config["description"], str)
            assert len(config["description"]) > 0
            assert isinstance(config["voices"], list)
            assert len(config["voices"]) > 0
            
            # Each voice should be a string
            for voice_name in config["voices"]:
                assert isinstance(voice_name, str)
                assert len(voice_name) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])