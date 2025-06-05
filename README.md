# 🎙️ VocalizeAgent - Text-to-Speech MCP Server 🗣️

[![GitHub](https://img.shields.io/badge/GitHub-harperreed-blue?logo=github)](https://github.com/harperreed)

A powerful MCP server that provides text-to-speech capabilities with emotion control and voice customization. Perfect for AI agents that need to express themselves with human-like voice characteristics.

## 📋 Summary

VocalizeAgent is an MCP (Machine Conversation Protocol) server that enables AI agents to speak text aloud with emotional expression. Built on pyttsx3, it offers:

- 🎭 Six emotion categories: cheerful, dramatic, friendly, professional, playful, and calm
- 🎛️ Full control over voice selection, speaking rate, and emotional tone
- 📚 Comprehensive documentation for effective voice emoting
- 🤖 Simple but powerful API for AI agents to vocalize their responses

This tool enhances AI interactions by adding an audio dimension to text-based communications, making digital assistants more engaging, expressive, and human-like.

## 🚀 How to Use

### Installation

```bash
# Clone the repository
git clone https://github.com/harperreed/vocalize-agent.git
cd vocalize-agent

# Set up Python environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .
```

### Running the Server

```bash
python main.py
```

### Using with AI Agents

VocalizeAgent provides three main tools:

#### 1. Basic Speech

```python
speak("Hello, I am your AI assistant")
```

#### 2. Emotional Speech

```python
speak("Great news! Your task completed successfully!", emotion="cheerful")
speak("Warning: Critical system alert detected", emotion="dramatic")
speak("How can I help you today?", emotion="friendly")
```

#### 3. Advanced Customization

```python
# Specific voice with custom rate
speak("This is an important announcement", voice="Bad News", rate=180)

# Combining emotion and rate
speak("Take a deep breath and relax", emotion="calm", rate=120)
```

#### 4. Discovery Tools

```python
# List available emotion categories
list_emotions()

# Browse all available voices
list_voices()

# Get comprehensive usage guide
voice_guide()
```

## 🔧 Technical Information

### Dependencies

- **Python**: 3.13+
- **MCP**: Machine Conversation Protocol for AI agent integration
- **pyttsx3**: Cross-platform text-to-speech library

### Architecture

VocalizeAgent is built on a FastMCP server that exposes TTS functionality through simple API calls. The system:

1. Organizes voices into emotional categories for easier selection
2. Adjusts speaking rates based on emotional context
3. Provides tools for voice discovery and documentation
4. Handles exceptions gracefully for robust operation

### Voice Emotion Categories

| Emotion | Description | Sample Voices |
|---------|-------------|---------------|
| 🎉 Cheerful | Upbeat, positive, energetic | Good News, Bubbles, Bells |
| 🎭 Dramatic | Theatrical, expressive | Bad News, Bahh, Cellos, Wobble |
| 🤝 Friendly | Warm, approachable | Fred, Albert, Flo, Grandma |
| 💼 Professional | Clear, authoritative | Eddy, Daniel, Anna |
| 🎪 Playful | Fun, quirky, entertaining | Boing, Bubbles, Bahh |
| 😌 Calm | Soothing, gentle, relaxed | Alice, Ellen, Amelie |

### API Reference

```python
speak(text: str, voice: str = None, emotion: str = None, rate: int = 150) -> str
```
- **text**: The text to speak
- **voice**: Specific voice name (e.g., "Fred", "Good News")
- **emotion**: Emotion category (cheerful, dramatic, friendly, professional, playful, calm)
- **rate**: Speaking rate in words per minute (default: 150)

```python
list_emotions() -> str
```
Lists all available emotion categories with descriptions

```python
list_voices() -> str
```
Lists all available TTS voices organized by emotion category

```python
voice_guide() -> str
```
Comprehensive documentation for effective voice usage

### Customization

VocalizeAgent can be extended by:
- Adding new emotion categories to the `VOICE_EMOTIONS` dictionary
- Adjusting rate modifiers for different emotional tones
- Implementing voice transformations for more expressive delivery

## 🔮 Future Development

- Support for additional TTS engines
- Voice pitch and volume control
- Audio file generation for offline use
- Multi-language support
- Voice cloning capabilities

---

Created by [Harper Reed](https://github.com/harperreed) | Licensed under MIT
