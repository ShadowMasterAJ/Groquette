#!/usr/bin/env python3

from typing import Optional
import pyaudio

BLACKHOLE_DEVICE_NAME = "BlackHole"

class AudioManager:
    """Simple audio device manager for voice agent integration."""
    
    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.blackhole_device_id: Optional[int] = None
        self._find_blackhole_device()
    
    def _find_blackhole_device(self):
        """Find BlackHole audio device."""
        for i in range(self.audio.get_device_count()):
            device_info = self.audio.get_device_info_by_index(i)
            if BLACKHOLE_DEVICE_NAME.lower() in device_info['name'].lower():
                self.blackhole_device_id = i
                print(f"🎤 Agent connected to device: {device_info['name']}")
                return
            
        print(f"🔇 Device not found")
    
    def is_blackhole_available(self) -> bool:
        """Check if BlackHole device is available."""
        return self.blackhole_device_id is not None
    
    def cleanup(self):
        """Clean up audio resources."""
        try:
            self.audio.terminate()
        except Exception as e:
            print(f"🔇 Error during audio cleanup: {e}")