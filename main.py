# ABOUTME: MCP server with text-to-speech capabilities using pyttsx3
# ABOUTME: Provides voice emoting tools for agents
from mcp.server.fastmcp import FastMCP
import pyttsx3
import threading
import logging
import atexit
import platform
from typing import Dict, List, Optional, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create an MCP server
mcp = FastMCP("VocalizeAgent")

# Thread lock for TTS operations
tts_lock = threading.Lock()

# Initialize TTS engine with error handling
try:
    tts_engine = pyttsx3.init()
    logger.info("TTS engine initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize TTS engine: {e}")
    tts_engine = None

# Voice cache for efficient lookups
_voice_cache: Dict[str, int] = {}
_available_voices: List = []

# Configuration for rate adjustments
RATE_CONFIG = {
    "min_rate": 50,
    "max_rate": 400,
    "default_rate": 150,
    "emotion_multipliers": {
        "dramatic": 1.2,
        "cheerful": 1.13, 
        "playful": 1.07,
        "professional": 1.0,
        "calm": 0.87,
        "friendly": 1.0
    }
}

# Platform-specific voice emotion categories
def get_voice_emotions_for_platform():
    """Get voice emotions configuration based on platform"""
    system = platform.system().lower()
    
    if system == "darwin":  # macOS
        return {
            "cheerful": {
                "description": "Upbeat, positive, and energetic voices",
                "voices": ["Good News", "Bubbles", "Bells"]
            },
            "dramatic": {
                "description": "Theatrical, expressive, and attention-grabbing voices", 
                "voices": ["Bad News", "Bahh", "Cellos", "Wobble", "Deranged"]
            },
            "friendly": {
                "description": "Warm, approachable, and conversational voices",
                "voices": ["Fred", "Albert", "Flo", "Grandma"]
            },
            "professional": {
                "description": "Clear, authoritative, and business-appropriate voices",
                "voices": ["Eddy", "Daniel", "Anna", "Alex"]
            },
            "playful": {
                "description": "Fun, quirky, and entertaining voices",
                "voices": ["Boing", "Bubbles", "Bahh"]
            },
            "calm": {
                "description": "Soothing, gentle, and relaxed voices", 
                "voices": ["Alice", "Ellen", "Amelie", "Samantha"]
            }
        }
    elif system == "windows":
        return {
            "cheerful": {
                "description": "Upbeat, positive, and energetic voices",
                "voices": ["Zira", "Eva"]
            },
            "dramatic": {
                "description": "Theatrical, expressive, and attention-grabbing voices", 
                "voices": ["David", "Mark"]
            },
            "friendly": {
                "description": "Warm, approachable, and conversational voices",
                "voices": ["Zira", "Hazel"]
            },
            "professional": {
                "description": "Clear, authoritative, and business-appropriate voices",
                "voices": ["David", "Mark"]
            },
            "playful": {
                "description": "Fun, quirky, and entertaining voices",
                "voices": ["Zira"]
            },
            "calm": {
                "description": "Soothing, gentle, and relaxed voices", 
                "voices": ["Hazel", "Eva"]
            }
        }
    else:  # Linux and others
        return {
            "cheerful": {
                "description": "Upbeat, positive, and energetic voices",
                "voices": ["default"]
            },
            "dramatic": {
                "description": "Theatrical, expressive, and attention-grabbing voices", 
                "voices": ["default"]
            },
            "friendly": {
                "description": "Warm, approachable, and conversational voices",
                "voices": ["default"]
            },
            "professional": {
                "description": "Clear, authoritative, and business-appropriate voices",
                "voices": ["default"]
            },
            "playful": {
                "description": "Fun, quirky, and entertaining voices",
                "voices": ["default"]
            },
            "calm": {
                "description": "Soothing, gentle, and relaxed voices", 
                "voices": ["default"]
            }
        }

# Initialize voice emotions for current platform
VOICE_EMOTIONS = get_voice_emotions_for_platform()


def cleanup_tts_engine():
    """Cleanup TTS engine on shutdown"""
    global tts_engine
    if tts_engine:
        try:
            tts_engine.stop()
            logger.info("TTS engine stopped successfully")
        except Exception as e:
            logger.error(f"Error stopping TTS engine: {e}")


def initialize_voice_cache():
    """Initialize voice cache for efficient lookups"""
    global _voice_cache, _available_voices
    
    if not tts_engine:
        logger.warning("TTS engine not available, skipping voice cache initialization")
        return
    
    try:
        voices = tts_engine.getProperty('voices')
        if not voices:
            logger.warning("No voices available on this system")
            return
        
        _available_voices = voices
        _voice_cache = {}
        
        # Build cache for efficient lookups
        for i, voice in enumerate(voices):
            voice_name = voice.name.lower()
            _voice_cache[voice_name] = i
            
            # Also cache partial matches for common variations
            words = voice_name.split()
            for word in words:
                if word not in _voice_cache:
                    _voice_cache[word] = i
        
        logger.info(f"Voice cache initialized with {len(voices)} voices")
        
        # Update emotion categories with actually available voices
        _update_emotion_categories_with_available_voices()
        
    except Exception as e:
        logger.error(f"Error initializing voice cache: {e}")


def _update_emotion_categories_with_available_voices():
    """Update emotion categories to only include actually available voices"""
    global VOICE_EMOTIONS
    
    for emotion, config in VOICE_EMOTIONS.items():
        available_voices_for_emotion = []
        
        for target_voice in config["voices"]:
            # Check if this voice exists in our cache
            found = False
            for cached_voice_name, index in _voice_cache.items():
                if target_voice.lower() in cached_voice_name:
                    available_voices_for_emotion.append(_available_voices[index].name)
                    found = True
                    break
            
            if not found:
                logger.debug(f"Voice '{target_voice}' not found for emotion '{emotion}'")
        
        # Update with available voices, or fallback to first available voice
        if available_voices_for_emotion:
            config["available_voices"] = available_voices_for_emotion
        else:
            config["available_voices"] = [_available_voices[0].name] if _available_voices else ["default"]
            logger.warning(f"No specific voices found for emotion '{emotion}', using fallback")


# Register cleanup function
atexit.register(cleanup_tts_engine)

# Initialize voice cache
initialize_voice_cache()

def find_voice_by_emotion_and_name(emotion: str = None, voice_name: str = None) -> int:
    """Find voice index by emotion category or specific voice name using cached lookups"""
    if not _available_voices:
        logger.warning("No voices available")
        return 0
    
    # If specific voice name provided, use cache for efficient lookup
    if voice_name:
        voice_key = voice_name.lower()
        if voice_key in _voice_cache:
            return _voice_cache[voice_key]
        
        # Fallback to partial matching
        for cached_name, index in _voice_cache.items():
            if voice_key in cached_name:
                return index
    
    # If emotion provided, find first matching voice from available voices for that emotion
    if emotion and emotion.lower() in VOICE_EMOTIONS:
        emotion_config = VOICE_EMOTIONS[emotion.lower()]
        available_voices = emotion_config.get("available_voices", emotion_config.get("voices", []))
        
        for target_voice in available_voices:
            voice_key = target_voice.lower()
            if voice_key in _voice_cache:
                return _voice_cache[voice_key]
            
            # Fallback to partial matching
            for cached_name, index in _voice_cache.items():
                if voice_key in cached_name:
                    return index
    
    return 0  # Default to first voice


def validate_speak_input(text: str, rate: int) -> Tuple[bool, str]:
    """Validate input parameters for speak function"""
    if not text or not text.strip():
        return False, "Text cannot be empty"
    
    if not isinstance(rate, (int, float)):
        return False, "Rate must be a number"
    
    if rate < RATE_CONFIG["min_rate"] or rate > RATE_CONFIG["max_rate"]:
        return False, f"Rate must be between {RATE_CONFIG['min_rate']} and {RATE_CONFIG['max_rate']} wpm"
    
    return True, ""


def calculate_emotion_rate(base_rate: int, emotion: str) -> int:
    """Calculate speaking rate based on emotion using configurable multipliers"""
    if not emotion or emotion.lower() not in RATE_CONFIG["emotion_multipliers"]:
        return base_rate
    
    multiplier = RATE_CONFIG["emotion_multipliers"][emotion.lower()]
    adjusted_rate = int(base_rate * multiplier)
    
    # Ensure rate stays within bounds
    return max(RATE_CONFIG["min_rate"], min(RATE_CONFIG["max_rate"], adjusted_rate))


# Unified text-to-speech tool
@mcp.tool()
def speak(text: str, voice: str = None, emotion: str = None, rate: int = 150) -> str:
    """Speak text aloud with optional voice and emotion control
    
    Args:
        text: The text to speak
        voice: Specific voice name to use (e.g. "Fred", "Good News", "Bad News")
        emotion: Emotion/vibe - "cheerful", "dramatic", "friendly", "professional", "playful", "calm"
        rate: Speaking rate in words per minute (default: 150, range: 50-400)
    
    Returns:
        Confirmation message about what was spoken
    """
    # Validate inputs
    is_valid, error_msg = validate_speak_input(text, rate)
    if not is_valid:
        logger.warning(f"Invalid input for speak function: {error_msg}")
        return f"❌ Error: {error_msg}"
    
    if not tts_engine:
        logger.error("TTS engine not available")
        return "❌ Error: Text-to-speech engine not available"
    
    # Use thread lock to ensure thread safety
    with tts_lock:
        try:
            logger.info(f"Speaking text: '{text[:50]}...' with emotion='{emotion}', voice='{voice}', rate={rate}")
            
            # Find appropriate voice based on voice name or emotion
            voice_index = find_voice_by_emotion_and_name(emotion, voice)
            
            if _available_voices and voice_index < len(_available_voices):
                tts_engine.setProperty('voice', _available_voices[voice_index].id)
                voice_used = _available_voices[voice_index].name
                logger.debug(f"Using voice: {voice_used} (index: {voice_index})")
            else:
                voice_used = "default"
                logger.warning(f"Could not find requested voice, using default")
            
            # Calculate final rate based on emotion
            final_rate = calculate_emotion_rate(rate, emotion)
            tts_engine.setProperty('rate', final_rate)
            
            # Speak the text
            tts_engine.say(text)
            tts_engine.runAndWait()
            
            # Build response message
            details = []
            if emotion:
                details.append(f"emotion: {emotion}")
            if voice:
                details.append(f"voice: {voice_used}")
            details.append(f"rate: {final_rate} wpm")
            
            detail_str = f" ({', '.join(details)})" if details else ""
            success_msg = f"🗣️ Spoke: '{text}'{detail_str}"
            logger.info(f"Successfully spoke text with {len(details)} parameters")
            return success_msg
            
        except Exception as e:
            error_msg = f"Error speaking text: {str(e)}"
            logger.error(error_msg)
            return f"❌ {error_msg}"


# Add tool to explore emotional voice options
@mcp.tool()
def list_emotions() -> str:
    """List available emotion categories for expressive speech
    
    Returns:
        Information about emotion categories and their voice characteristics
    """
    emotion_guide = ["🎭 EMOTION CATEGORIES FOR EXPRESSIVE SPEECH:", ""]
    
    for emotion, info in VOICE_EMOTIONS.items():
        emotion_guide.append(f"🎯 {emotion.upper()}")
        emotion_guide.append(f"   Description: {info['description']}")
        emotion_guide.append(f"   Sample voices: {', '.join(info['voices'])}")
        emotion_guide.append("")
    
    emotion_guide.append("💡 USAGE EXAMPLES:")
    emotion_guide.append("   speak('Great job!', emotion='cheerful')")
    emotion_guide.append("   speak('Breaking news...', emotion='dramatic')")
    emotion_guide.append("   speak('How can I help?', emotion='professional')")
    emotion_guide.append("   speak('Hello there!', voice='Fred')")
    emotion_guide.append("   speak('Urgent message!', voice='Bad News', rate=200)")
    
    return "\n".join(emotion_guide)


# Add tool to list available voices (simplified for emotion-focused workflow)
@mcp.tool()
def list_voices() -> str:
    """List available text-to-speech voices with emotion categories
    
    Returns:
        Information about available voices organized by emotion
    """
    try:
        if not _available_voices:
            logger.warning("No voices available in cache")
            return "❌ No voices available on this system"
        
        platform_name = platform.system()
        
        # Show emotion categories first
        result = [
            f"🎭 VOICE GUIDE FOR {platform_name.upper()}:",
            f"🎙️ {len(_available_voices)} voices available on your system",
            "",
            "🎯 RECOMMENDED EMOTIONS:"
        ]
        
        for emotion, info in VOICE_EMOTIONS.items():
            available_voices = info.get("available_voices", [])
            if available_voices and available_voices != ["default"]:
                result.append(f"• {emotion}: {info['description']} ({len(available_voices)} voices)")
            else:
                result.append(f"• {emotion}: {info['description']} (using fallback)")
        
        result.append("\n" + "="*60)
        result.append("🎯 VOICES BY EMOTION CATEGORY:")
        result.append("")
        
        # Show available voices for each emotion category
        for emotion, info in VOICE_EMOTIONS.items():
            available_voices = info.get("available_voices", info.get("voices", []))
            if available_voices:
                result.append(f"🎭 {emotion.upper()}:")
                for voice_name in available_voices[:5]:  # Limit to 5 per category
                    if voice_name in _voice_cache:
                        index = _voice_cache[voice_name.lower()]
                        result.append(f"   {index}: {voice_name}")
                if len(available_voices) > 5:
                    result.append(f"   ... and {len(available_voices) - 5} more")
                result.append("")
        
        result.append("💡 USAGE:")
        result.append("   speak('Hello!', emotion='friendly')")
        result.append("   speak('Alert!', emotion='dramatic')")
        result.append("   speak('Calm down', emotion='calm')")
        
        return "\n".join(result)
        
    except Exception as e:
        error_msg = f"Error listing voices: {str(e)}"
        logger.error(error_msg)
        return f"❌ {error_msg}"


# Add comprehensive usage guide for agents
@mcp.tool()
def voice_guide() -> str:
    """Complete guide for AI agents on using voice capabilities effectively
    
    Returns:
        Comprehensive documentation and best practices for voice emoting
    """
    guide = [
        "🎙️ VOCALIZE AGENT - VOICE EMOTING GUIDE FOR AI AGENTS",
        "=" * 60,
        "",
        "🎯 PURPOSE:",
        "This MCP server enables you to express emotions and personality through voice,",
        "making interactions more engaging and human-like. Use voice to match your",
        "emotional state, emphasize important information, or create atmosphere.",
        "",
        "🗣️ MAIN FUNCTION: speak(text, voice=None, emotion=None, rate=150)",
        "",
        "📋 EMOTION CATEGORIES & WHEN TO USE:",
        "",
        "🎉 CHEERFUL - Use when:",
        "   • Celebrating success or achievements",
        "   • Sharing good news or positive updates", 
        "   • Expressing excitement or enthusiasm",
        "   • Encouraging or motivating users",
        "   Example: speak('Congratulations! Task completed successfully!', emotion='cheerful')",
        "",
        "🎭 DRAMATIC - Use when:",
        "   • Making important announcements",
        "   • Highlighting critical information or warnings",
        "   • Creating suspense or emphasis",
        "   • Drawing attention to key points",
        "   Example: speak('BREAKING: Critical system alert detected!', emotion='dramatic')",
        "",
        "🤝 FRIENDLY - Use when:",
        "   • Casual conversation and greetings",
        "   • Providing help or assistance",
        "   • Building rapport with users",
        "   • General day-to-day interactions",
        "   Example: speak('Hi there! How can I help you today?', emotion='friendly')",
        "",
        "💼 PROFESSIONAL - Use when:",
        "   • Business communications",
        "   • Formal presentations or reports",
        "   • Technical explanations",
        "   • Official announcements",
        "   Example: speak('The quarterly review meeting is scheduled for 3 PM.', emotion='professional')",
        "",
        "🎪 PLAYFUL - Use when:",
        "   • Making jokes or being humorous",
        "   • Engaging in fun activities",
        "   • Working with children or in casual contexts",
        "   • Adding levity to conversations",
        "   Example: speak('Oops! That was a silly mistake!', emotion='playful')",
        "",
        "😌 CALM - Use when:",
        "   • Providing reassurance or comfort",
        "   • Delivering meditation or relaxation content",
        "   • Discussing sensitive topics",
        "   • De-escalating tense situations",
        "   Example: speak('Take a deep breath. Everything will be okay.', emotion='calm')",
        "",
        "🎛️ ADVANCED USAGE:",
        "",
        "• Specific Voices: speak('Hello!', voice='Fred') - Use named voices for consistency",
        "• Rate Control: speak('Fast update!', emotion='dramatic', rate=200) - Adjust speed",
        "• Voice Override: speak('Special voice', voice='Bad News') - Direct voice selection",
        "",
        "💡 BEST PRACTICES FOR AI AGENTS:",
        "",
        "1. MATCH EMOTION TO CONTENT:",
        "   - Good news → cheerful",
        "   - Warnings → dramatic", 
        "   - Instructions → professional",
        "   - Comfort → calm",
        "",
        "2. VARY YOUR VOICE:",
        "   - Don't use the same emotion for everything",
        "   - Switch between voices to keep interactions dynamic",
        "   - Use dramatic sparingly for maximum impact",
        "",
        "3. CONSIDER CONTEXT:",
        "   - Professional settings → professional/friendly",
        "   - Casual chat → friendly/playful",
        "   - Emergency alerts → dramatic",
        "   - Relaxation → calm",
        "",
        "4. EMOTIONAL PROGRESSION:",
        "   - Start conversations friendly",
        "   - Escalate to dramatic for important points",
        "   - Return to calm for conclusions",
        "",
        "🔧 DISCOVERY TOOLS:",
        "• list_emotions() - Show all emotion categories with descriptions",
        "• list_voices() - Browse available voices organized by emotion",
        "• voice_guide() - This comprehensive guide",
        "",
        "🎯 QUICK REFERENCE:",
        "speak('text')                          # Basic speech",
        "speak('text', emotion='cheerful')      # Emotion-based",
        "speak('text', voice='Fred')            # Specific voice", 
        "speak('text', emotion='calm', rate=120) # Full control",
        "",
        "Remember: Voice is a powerful tool for creating connection and conveying",
        "meaning beyond words. Use it thoughtfully to enhance your communication!"
    ]
    
    return "\n".join(guide)


def main():
    """Main entry point for the vocalize MCP server"""
    import sys
    
    logger.info("Starting VocalizeAgent MCP server...")
    try:
        mcp.run()
    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
