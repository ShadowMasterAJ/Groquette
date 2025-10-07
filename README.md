# 🎙️ Groquette

> An AI voice assistant that automatically joins Google Meet calls and facilitates engineering demo meetings.

Groquette (pronounced "gro-ket") is a meeting facilitator bot that uses Groq's AI stack to join video calls, listen to conversations, and participate as a moderator.

## What It Does

- Automatically joins Google Meet using Selenium givent the google meets code/link
- Uses Groq's Whisper for speech-to-text, Llama for language processing, and PlayAI for text-to-speech
- Moderates meetings by facilitating demos, prompting questions, and managing flow
- Can mute/unmute itself based on meeting context and only responds when mentioned
- Routes audio through BlackHole virtual audio driver

## Setup

### Prerequisites

- Python 3.8+
- Google Chrome + ChromeDriver
- [BlackHole](https://existential.audio/blackhole/) virtual audio driver (macOS: `brew install blackhole-2ch`)
- Groq API key ([get one here](https://console.groq.com/))
- LiveKit account ([sign up here](https://cloud.livekit.io/))

### Installation

1. Clone the repo and install dependencies:
```bash
git clone https://github.com/ShadowMasterAJ/Groquette.git
cd Groquette
pip install -r requirements.txt
```

2. Create a `.env` file with your credentials:
```env
GOOGLE_EMAIL=your-email@gmail.com
GOOGLE_PASSWORD=your-password
GROQ_API_KEY=your-groq-api-key
```

3. Test BlackHole setup:
```bash
python -c "from src.audio.blackhole import test_blackhole_devices; test_blackhole_devices()"
```

## Usage

Run with a Google Meet code:
```bash
python main.py abc-defg-hij
```

Or run and enter the code when prompted:
```bash
python main.py
```

**Controls:**
- Press 'r' + Enter to restart
- Press 'q' + Enter or Ctrl+C to exit

## How It Works

The project has three main parts:
- **Meeting Joiner** (`src/meeting/`) - Selenium automation for joining Google Meet
- **Voice Agent** (`src/ai/`) - LiveKit agent using Groq's AI stack
- **IPC Bridge** (`src/meeting/ipc_commands.py`) - Lets the voice agent control the meeting UI

## Development

```bash
make format      # Format code with black and isort
make lint        # Check code with flake8
make all-checks  # Run all checks
```

## License

MIT License - see [LICENSE](LICENSE) file.
