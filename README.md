# 🎙️ VocalizeAgent - Text-to-Speech MCP Server 🗣️

[![GitHub](https://img.shields.io/badge/GitHub-harperreed-blue?logo=github)](https://github.com/harperreed)

A powerful MCP server that provides text-to-speech capabilities with emotion control and voice customization. Perfect for AI agents that need to express themselves with human-like voice characteristics.

## 📋 Summary

VocalizeAgent is an MCP (Machine Conversation Protocol) server that enables AI agents to speak text aloud with emotional expression. Built with support for multiple TTS engines (pyttsx3, gTTS, and ElevenLabs), it offers:

- 🎭 Six emotion categories: cheerful, dramatic, friendly, professional, playful, and calm
- 🎛️ Full control over voice selection, speaking rate, and emotional tone
- 🎯 Multiple TTS engines: pyttsx3 (offline), gTTS (online with accents), ElevenLabs (AI voices)
- 🔄 Automatic fallback when optional dependencies or API keys are not available
- 📚 Comprehensive documentation for effective voice emoting
- 🤖 Simple but powerful API for AI agents to vocalize their responses

This tool enhances AI interactions by adding an audio dimension to text-based communications, making digital assistants more engaging, expressive, and human-like.

## 🚀 How to Use

### Installation

```bash
# Clone the repository
git clone https://github.com/harperreed/vocalize-mcp.git
cd vocalize-mcp

# Install with uv (recommended) - full installation with all engines
uv sync

# OR install simple version (pyttsx3 only)
uv sync --only-deps simple

# OR install with pip
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .                    # Full installation
pip install -e .[simple]           # Simple installation (pyttsx3 only)
```

### TTS Engine Selection

Control which TTS engine to use with the `TTS_ENGINE` environment variable:

```bash
# Use pyttsx3 (default, offline)
TTS_ENGINE=pyttsx3 uv run python main.py

# Use gTTS (online, requires --extra gtts)
TTS_ENGINE=gtts uv run python main.py

# Use ElevenLabs (AI voices, requires --extra elevenlabs and API key)
ELEVENLABS_API_KEY=your_api_key_here TTS_ENGINE=elevenlabs uv run python main.py
```

**Engine Features:**

- **pyttsx3**: Offline engine with system voices and rate control
- **gTTS**: Online Google TTS with accent variations for emotions
- **ElevenLabs**: AI-powered voices with advanced emotional control

### ElevenLabs Configuration

For ElevenLabs engine, set these environment variables:

```bash
export ELEVENLABS_API_KEY="your_api_key_here"
export ELEVENLABS_VOICE_ID="JBFqnCBsd6RMkjVDRZzb"  # Optional, defaults to George
```

**Or create a `.env` file** (automatically loaded):

```bash
ELEVENLABS_API_KEY=your_api_key_here
ELEVENLABS_VOICE_ID=JBFqnCBsd6RMkjVDRZzb
```

- Get your API key from [ElevenLabs Dashboard](https://elevenlabs.io/app/speech-synthesis)
- Voice IDs can be found in your ElevenLabs voice library
- Uses the `eleven_flash_v2_5` model for fast, high-quality synthesis
- Environment variables override `.env` file values

## 🔗 Install as MCP Server

To use VocalizeAgent with Claude Desktop or other MCP clients:

### 1. Install the Package

```bash
# Clone and install the package
git clone https://github.com/harperreed/vocalize-mcp.git
cd vocalize-mcp
uv sync  # Full installation with all engines by default
```

### 2. Configure MCP Client

#### Claude Desktop

Add to your MCP client configuration (e.g., Claude Desktop's config):

```json
{
    "mcpServers": {
        "vocalize": {
            "command": "uvx",
            "args": [
                "--from",
                "git+https://github.com/2389-research/vocalize-mcp",
                "vocalize-mcp"
            ],
            "env": {
                "TTS_ENGINE": "gtts"
            }
        }
    }
}
```

or

```json
{
    "mcpServers": {
        "vocalize": {
            "command": "uvx",
            "args": [
                "--from",
                "git+https://github.com/2389-research/vocalize-mcp",
                "vocalize-mcp"
            ],
            "env": {
                "TTS_ENGINE": "gtts",
                "ELEVENLABS_API_KEY": "sk_xxx",
                "ELEVENLABS_VOICE_ID": "JBFqnCBsd6RMkjVDRZzb"
            }
        }
    }
}
```

#### Claude Code

```shell
claude mcp add-json vocalize '{"type":"stdio","command":"uvx","args":["--from","git+https://github.com/2389-research/vocalize-mcp","vocalize-mcp"],"ENV":{"TTS_ENGINE":"gtts"}}'
```

Eleven Labs

```shell
claude mcp add-json vocalize '{"type":"stdio","command":"uvx","args":["--from","git+https://github.com/2389-research/vocalize-mcp","vocalize-mcp"],"ENV":{"ELEVENLABS_API_KEY:","sk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", "ELEVENLABS_VOICE_ID":"JBFqnCBsd6RMkjVDRZzb","TTS_ENGINE":"elevenlabs"}}'
```

### 3. Alternative Installation Methods

**Using Python directly:**

```json
{
    "mcpServers": {
        "vocalize": {
            "command": "python",
            "args": ["/path/to/vocalize-mcp/main.py"],
            "env": {
                "TTS_ENGINE": "elevenlabs",
                "ELEVENLABS_API_KEY": "your_api_key"
            }
        }
    }
}
```

**Using executable script:**

```json
{
    "mcpServers": {
        "vocalize": {
            "command": "/path/to/vocalize-mcp/.venv/bin/vocalize-mcp",
            "env": {
                "TTS_ENGINE": "gtts"
            }
        }
    }
}
```

### 4. Available Tools

Once connected, you'll have access to these MCP tools:

- `speak()` - Generate speech with emotional control
- `list_voices()` - Browse available voices for current engine
- `list_emotions()` - See emotion categories and descriptions
- `voice_guide()` - Complete usage documentation

### Running the Server

```bash
# With uv (recommended)
uv run python main.py

# OR with activated virtual environment
python main.py
```

### Testing

```bash
# Run all tests
uv run pytest

# Run specific test suites
uv run pytest test_voice.py          # Unit tests
uv run pytest test_integration.py    # Integration tests
uv run pytest test_improvements.py   # Improvement validation

# Run tests excluding slow audio tests
uv run pytest -m "not slow"
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
- **uv**: Fast Python package manager (recommended) - [Install uv](https://github.com/astral-sh/uv)
- **MCP**: Machine Conversation Protocol for AI agent integration
- **pyttsx3**: Cross-platform text-to-speech library (included by default)
- **gTTS**: Google Text-to-Speech (included by default)
- **pygame**: Audio playback for gTTS and ElevenLabs (included by default)
- **elevenlabs**: ElevenLabs AI voices (included by default)
- **python-dotenv**: Environment variable loading (included by default)

### Why uv?

This project uses [uv](https://github.com/astral-sh/uv) for dependency management because it's:

- ⚡ **10-100x faster** than pip for installing packages
- 🔒 **Reliable** with deterministic dependency resolution
- 🛠️ **Simple** with built-in virtual environment management
- 📦 **Compatible** with standard Python packaging

### Architecture

VocalizeAgent is built on a FastMCP server that exposes TTS functionality through simple API calls. The system:

1. **Multi-engine support**: Dynamically selects TTS engine based on environment variable
2. **Graceful fallback**: Automatically falls back to pyttsx3 when gTTS is not available
3. **Emotion mapping**: Maps emotions to appropriate voices (pyttsx3) or accents (gTTS)
4. **Voice organization**: Organizes voices into emotional categories for easier selection
5. **Rate adjustment**: Adjusts speaking rates based on emotional context
6. **Discovery tools**: Provides tools for voice discovery and documentation
7. **Exception handling**: Handles errors gracefully for robust operation

#### TTS Engine Comparison

| Feature             | pyttsx3           | gTTS                              | ElevenLabs                                    |
| ------------------- | ----------------- | --------------------------------- | --------------------------------------------- |
| **Connection**      | Offline           | Online (requires internet)        | Online (requires internet + API key)          |
| **Voices**          | System voices     | Google voices with accents        | AI-generated voices                           |
| **Emotion mapping** | Voice selection   | Accent variation (UK, AU, CA, US) | Voice settings (stability, style, similarity) |
| **Rate control**    | Full rate control | Fixed rate                        | Fixed rate                                    |
| **Latency**         | Instant           | Network dependent                 | Network dependent                             |
| **Quality**         | System dependent  | Consistent high quality           | Premium AI quality                            |
| **Cost**            | Free              | Free                              | Paid (API credits)                            |
| **Voice variety**   | Limited to system | Accent variations                 | Unlimited AI voices                           |

### Voice Emotion Categories

| Emotion         | Description                 | Sample Voices                  |
| --------------- | --------------------------- | ------------------------------ |
| 🎉 Cheerful     | Upbeat, positive, energetic | Good News, Bubbles, Bells      |
| 🎭 Dramatic     | Theatrical, expressive      | Bad News, Bahh, Cellos, Wobble |
| 🤝 Friendly     | Warm, approachable          | Fred, Albert, Flo, Grandma     |
| 💼 Professional | Clear, authoritative        | Eddy, Daniel, Anna             |
| 🎪 Playful      | Fun, quirky, entertaining   | Boing, Bubbles, Bahh           |
| 😌 Calm         | Soothing, gentle, relaxed   | Alice, Ellen, Amelie           |

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
