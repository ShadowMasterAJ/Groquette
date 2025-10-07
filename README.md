# 🎙️ Groquette

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> An AI-powered voice assistant that automatically joins Google Meet calls and facilitates engineering demo meetings using Groq's AI stack.

Groquette (pronounced "grocket") is an intelligent meeting facilitator designed specifically for Friday engineering demo meetings. It uses cutting-edge AI technology to join video calls, listen to conversations, and actively participate as a meeting moderator—keeping demos flowing, discussions lively, and ensuring every voice is heard.

## ✨ Features

- 🤖 **Automated Meeting Join**: Automatically joins Google Meet calls using Selenium WebDriver
- 🎤 **Voice-Enabled AI**: Real-time speech-to-text, natural language processing, and text-to-speech using Groq's AI stack
- 🎧 **Virtual Audio Integration**: Uses BlackHole virtual audio driver for seamless audio routing
- 💬 **Intelligent Moderation**: Actively facilitates demos, prompts questions, and manages meeting flow
- 🔄 **Live Interaction**: Can mute/unmute itself and respond to meeting participants in real-time
- 🚀 **LiveKit Integration**: Built on LiveKit Agents for robust real-time communication

## 🏗️ Architecture

Groquette consists of three main components:

1. **Meeting Joiner** (`src/meeting/meet_joiner.py`)
   - Selenium-based automation to join Google Meet
   - Configures audio devices and meeting preferences
   - Monitors meeting state and handles reconnections

2. **Voice Agent** (`src/ai/voice_agent.py`)
   - LiveKit Agents-based voice assistant
   - Integrates Groq's Whisper STT, Llama LLM, and PlayAI TTS
   - Manages conversation flow and meeting facilitation

3. **IPC Bridge** (`src/meeting/ipc_commands.py`)
   - File-based inter-process communication
   - Allows voice agent to control meeting UI (mute/unmute, etc.)
   - Enables coordination between Selenium and LiveKit processes

## 📋 Prerequisites

Before you begin, ensure you have the following:

- **Python 3.8+** installed
- **Google Chrome** browser
- **ChromeDriver** (matching your Chrome version)
- **BlackHole** virtual audio driver ([Download](https://existential.audio/blackhole/))
- **Google Account** with access to Google Meet
- **Groq API Key** ([Get one here](https://console.groq.com/))
- **LiveKit Cloud Account** ([Sign up here](https://cloud.livekit.io/))

### macOS Users

```bash
# Install BlackHole using Homebrew
brew install blackhole-2ch
```

### Linux/Windows Users

BlackHole is macOS-specific. For other platforms, you'll need equivalent virtual audio cable software:
- **Linux**: PulseAudio with null sinks or JACK Audio
- **Windows**: VB-AUDIO Virtual Cable or similar

## 🚀 Installation

1. **Clone the repository**

```bash
git clone https://github.com/ShadowMasterAJ/Groquette.git
cd Groquette
```

2. **Install dependencies**

```bash
make install
# or
pip install -r requirements.txt
```

3. **Set up environment variables**

Create a `.env` file in the root directory with the following:

```env
# Google Account Credentials
GOOGLE_EMAIL=your-email@gmail.com
GOOGLE_PASSWORD=your-password

# Groq API Key
GROQ_API_KEY=your-groq-api-key

# LiveKit Credentials
LIVEKIT_URL=wss://your-livekit-server.livekit.cloud
LIVEKIT_API_KEY=your-api-key
LIVEKIT_API_SECRET=your-api-secret
```

4. **Configure BlackHole audio**

Ensure BlackHole is installed and recognized by your system:

```bash
# Test BlackHole devices
python -c "from src.audio.blackhole import test_blackhole_devices; test_blackhole_devices()"
```

## 🎯 Usage

### Basic Usage

Run Groquette with a Google Meet code:

```bash
python main.py abc-defg-hij
```

Or run without arguments to be prompted:

```bash
python main.py
# Enter Google Meet code (xxx-xxxx-xxx): abc-defg-hij
```

### Meeting Controls

Once Groquette joins the meeting, you can:

- **Press 'r' + Enter**: Restart the application
- **Press 'q' + Enter** or **Ctrl+C**: Leave the meeting and exit

### Voice Agent Commands

Groquette responds to natural language commands during meetings:

- "Groquette, what do you think?" - Unmutes and responds
- "Let me share my screen" - Automatically mutes
- Natural conversation flow with automatic mute/unmute management

## 🧪 Development

### Code Quality Tools

This project uses several tools to maintain code quality:

```bash
# Run all checks
make all-checks

# Format code
make format

# Fix linting issues
make lint-fix

# Run pre-commit hooks
make pre-commit
```

### Project Structure

```
Groquette/
├── main.py                 # Main entry point
├── utils.py                # Utility functions
├── requirements.txt        # Python dependencies
├── Makefile               # Development commands
├── pyproject.toml         # Build and tool configuration
└── src/
    ├── ai/
    │   ├── voice_agent.py      # LiveKit voice agent
    │   ├── llm.py              # Custom LLM component
    │   └── system_prompt.txt   # Agent personality/instructions
    ├── audio/
    │   └── blackhole.py        # Audio device management
    ├── meeting/
    │   ├── meet_joiner.py      # Google Meet automation
    │   ├── ipc_commands.py     # Inter-process communication
    │   └── utils.py            # Meeting utilities
    └── utils/
        └── __init__.py
```

### Key Technologies

- **[LiveKit Agents](https://docs.livekit.io/agents/)**: Real-time voice agent framework
- **[Groq](https://groq.com/)**: Ultra-fast AI inference
  - Whisper Large V3 Turbo (Speech-to-Text)
  - Llama 4 Maverick (Language Model)
  - PlayAI TTS (Text-to-Speech)
- **[Selenium](https://www.selenium.dev/)**: Browser automation
- **[BlackHole](https://existential.audio/blackhole/)**: Virtual audio routing

## 🔧 Troubleshooting

### BlackHole Not Found

If you see "BlackHole device not found":

1. Verify BlackHole is installed: Check System Preferences > Sound
2. Restart your computer after installing BlackHole
3. Run the test command: `python -c "from src.audio.blackhole import test_blackhole_devices; test_blackhole_devices()"`

### ChromeDriver Version Mismatch

If you see ChromeDriver compatibility errors:

1. Check your Chrome version: `google-chrome --version` or `chrome://version`
2. Download matching ChromeDriver from [here](https://chromedriver.chromium.org/downloads)
3. Add ChromeDriver to your PATH

### Meeting Join Failures

If Groquette can't join meetings:

1. Verify Google credentials in `.env`
2. Check if 2FA is enabled (may need app-specific password)
3. Ensure the meeting code format is correct: `xxx-xxxx-xxx`
4. Check if the meeting has already started or allows guests

### Voice Agent Not Speaking

If the voice agent isn't responding:

1. Verify Groq API key is valid
2. Check LiveKit credentials are correct
3. Ensure BlackHole audio routing is working
4. Check console for error messages

### IPC Communication Issues

If voice commands don't affect the meeting UI:

1. Check `/tmp/groquette_commands.json` permissions
2. Verify both processes (Selenium and LiveKit) are running
3. Look for IPC-related errors in console output

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Make your changes
4. Run code quality checks (`make all-checks`)
5. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
6. Push to the branch (`git push origin feature/AmazingFeature`)
7. Open a Pull Request

### Code Style

This project follows:
- **Black** for code formatting
- **isort** for import sorting
- **flake8** for linting
- **mypy** for type checking

Run `make format-all` before committing to ensure compliance.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with ❤️ by the Groq team
- Powered by [Groq's](https://groq.com/) blazing-fast AI inference
- Uses [LiveKit's](https://livekit.io/) real-time communication platform
- Inspired by the need for better engineering demo meetings

## 📧 Support

For questions, issues, or feature requests:
- Open an issue on [GitHub](https://github.com/ShadowMasterAJ/Groquette/issues)
- Check existing issues for similar problems
- Provide detailed information about your setup and error messages

---

**Note**: This is an experimental project. Use responsibly and ensure you have permission before deploying AI agents in professional meetings.
