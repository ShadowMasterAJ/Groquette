"""Voice agent implementation for Google Meet calls using Groq's complete AI stack."""

import asyncio
import os
import sys
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from livekit import agents, rtc
from livekit.agents import Agent, AgentSession, JobProcess
from livekit.plugins import groq, silero
from llm import CustomGroqLLM

from src.audio.blackhole import set_mic_to_blackhole, set_speaker_to_blackhole

load_dotenv()

# Add parent directory to path for imports when running as standalone script
# Get the absolute path to the project root (Groquette directory)
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent.parent
sys.path.insert(0, str(project_root))


class VoiceAgent(Agent):
    """Simple voice agent for Google Meet calls using Groq's complete AI stack."""

    def __init__(self) -> None:
        """Initialize the voice agent."""
        instructions = self._load_system_prompt()
        if instructions is None:
            instructions = "You are a helpful AI assistant in a video call."
        super().__init__(instructions=instructions)

    def _load_system_prompt(self) -> Optional[str]:
        """Load system prompt from file."""
        try:
            prompt_path = os.path.join(os.path.dirname(__file__), "system_prompt.txt")
            with open(prompt_path, "r", encoding="utf-8") as f:
                return f.read().strip()
        except Exception as e:
            print(f"❌ Error loading system prompt: {e}")
            return "You are a helpful AI assistant in a video call."


async def entrypoint(ctx: agents.JobContext) -> None:
    """Main entrypoint for the voice agent configured for console operation."""
    try:
        print("🤖 Starting voice agent from console...")
        print(f"🔗 Room name: {ctx.room.name}")
        print(f"🆔 Room ID: {ctx.room.sid}")

        # Configure audio devices to use BlackHole
        print("🎤 Configuring audio devices...")
        mic_id = set_mic_to_blackhole()
        speaker_id = set_speaker_to_blackhole()

        if mic_id is None or speaker_id is None:
            print("⚠️ Warning: BlackHole audio devices not configured properly")
            print("⚠️ Continuing with system default audio devices...")
        else:
            print("✅ BlackHole audio devices configured successfully")

        # Get API keys from environment
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            print("❌ GROQ_API_KEY not found in environment variables")
            return

        await ctx.connect()
        print("✅ Connected to room successfully")

        session: AgentSession = AgentSession(
            stt=groq.STT(
                model="whisper-large-v3-turbo", language="en", api_key=groq_api_key
            ),
            llm=CustomGroqLLM(
                api_key=groq_api_key,
                model="meta-llama/llama-4-maverick-17b-128e-instruct",
                room=ctx.room,
            ),
            tts=groq.TTS(
                model="playai-tts", voice="Arista-PlayAI", api_key=groq_api_key
            ),
            vad=silero.VAD.load(),
        )

        # Create and start the agent
        agent = VoiceAgent()
        print("🚀 Starting agent session...")
        await session.start(agent=agent, room=ctx.room)

        # Generate initial greeting
        print("👋 Generating initial greeting...")
        await session.generate_reply()
        print("🔄 Agent is now active and listening for audio input...")

        # Keep the agent running
        try:
            while ctx.room.connection_state == rtc.ConnectionState.CONN_CONNECTED:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Agent stopped by user")

    except Exception as e:
        print(f"❌ Error in voice agent: {e}")
        import traceback

        traceback.print_exc()
    finally:
        print("🔄 Cleaning up agent session...")


def prewarm(proc: JobProcess) -> None:
    """Load the VAD model during prewarm for faster startup."""
    proc.userdata["vad"] = silero.VAD.load()


def run_agent() -> None:
    """Run the voice agent with LiveKit CLI for console operation."""
    print("🎯 Starting LiveKit voice agent via console...")

    # Configure worker options for console operation
    worker_options = agents.WorkerOptions(
        entrypoint_fnc=entrypoint, prewarm_fnc=prewarm
    )

    # Run the agent using LiveKit CLI
    agents.cli.run_app(worker_options)


if __name__ == "__main__":
    run_agent()
