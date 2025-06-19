"""Simple audio device manager for voice agent integration."""

from typing import Optional

import pyaudio

BLACKHOLE_DEVICE_NAME = "BlackHole"


class AudioManager:
    """Audio device manager for voice agent integration."""

    def __init__(self) -> None:
        """Initialize the audio manager."""
        self.audio = pyaudio.PyAudio()
        self.blackhole_device_id: Optional[int] = None
        self._find_blackhole_device()

    def _find_blackhole_device(self) -> None:
        """Find BlackHole audio device."""
        for i in range(self.audio.get_device_count()):
            device_info = self.audio.get_device_info_by_index(i)
            device_name = device_info["name"]
            if (
                isinstance(device_name, str)
                and BLACKHOLE_DEVICE_NAME.lower() in device_name.lower()
            ):
                self.blackhole_device_id = i
                print(f"🎤 Agent connected to device: {device_info['name']}")
                return

        print("🔇 Device not found")

    def is_blackhole_available(self) -> bool:
        """Check if BlackHole device is available."""
        return self.blackhole_device_id is not None

    def cleanup(self) -> None:
        """Clean up audio resources."""
        try:
            self.audio.terminate()
        except Exception as e:
            print(f"🔇 Error during audio cleanup: {e}")
