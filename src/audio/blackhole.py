"""Audio device selector for BlackHole virtual audio driver.

Provides functions to set microphone and speaker to BlackHole devices.
"""

import logging
import time
from typing import Optional

import sounddevice as sd

logger = logging.getLogger(__name__)


def list_audio_devices() -> None:
    """List all available audio devices for debugging."""
    print("\n=== AUDIO DEVICES ===")
    try:
        devices = sd.query_devices()
        print(f"Total devices found: {len(devices)}")
        for i, device in enumerate(devices):
            print(f"Device {i}: {device['name']}")
            print(
                f"  Channels: in={device['max_input_channels']}, "
                f"out={device['max_output_channels']}"
            )
            print(f"  Sample rate: {device['default_samplerate']}")

        default_in, default_out = sd.default.device
        print(f"\nCurrent default input: {default_in}")
        print(f"Current default output: {default_out}")
    except Exception as e:
        print(f"Error listing devices: {e}")
    print("=== END DEVICES ===\n")


def find_blackhole_device(device_type: str = "input") -> Optional[int]:
    """Find BlackHole device by name.

    Args:
        device_type: "input" for microphone, "output" for speaker

    Returns:
        Device ID if found, None otherwise
    """
    try:
        devices = sd.query_devices()
        for i, device in enumerate(devices):
            device_name = device["name"].lower()

            # Look for BlackHole in device name
            if "blackhole" in device_name:
                if device_type == "input" and device["max_input_channels"] > 0:
                    logger.info(
                        f"Found BlackHole input device: {device['name']} (ID: {i})"
                    )
                    return i
                elif device_type == "output" and device["max_output_channels"] > 0:
                    logger.info(
                        f"Found BlackHole output device: {device['name']} (ID: {i})"
                    )
                    return i

    except Exception as e:
        logger.error(f"Error finding BlackHole device: {e}")

    return None


def set_mic_to_blackhole() -> Optional[int]:
    """Set microphone input to BlackHole device.

    Returns:
        BlackHole input device ID if successful, None otherwise
    """
    blackhole_input = find_blackhole_device("input")

    if blackhole_input is not None:
        try:
            # Verify the device works by checking its properties
            device_info = sd.query_devices(blackhole_input)
            if device_info["max_input_channels"] > 0:
                # Set as default input device
                sd.default.device[0] = blackhole_input
                logger.info(
                    f"Successfully set microphone to BlackHole: {device_info['name']}"
                )
                return blackhole_input
            else:
                logger.error("BlackHole device found but has no input channels")
        except Exception as e:
            logger.error(f"Failed to set BlackHole as input device: {e}")
    else:
        logger.error(
            "BlackHole input device not found. Make sure BlackHole is installed."
        )
        list_audio_devices()  # Show available devices for debugging

    return None


def set_speaker_to_blackhole() -> Optional[int]:
    """Set speaker output to BlackHole device.

    Returns:
        BlackHole output device ID if successful, None otherwise
    """
    blackhole_output = find_blackhole_device("output")

    if blackhole_output is not None:
        try:
            # Verify the device works by checking its properties
            device_info = sd.query_devices(blackhole_output)
            if device_info["max_output_channels"] > 0:
                # Set as default output device
                sd.default.device[1] = blackhole_output
                logger.info(
                    f"Successfully set speaker to BlackHole: {device_info['name']}"
                )
                return blackhole_output
            else:
                logger.error("BlackHole device found but has no output channels")
        except Exception as e:
            logger.error(f"Failed to set BlackHole as output device: {e}")
    else:
        logger.error(
            "BlackHole output device not found. Make sure BlackHole is installed."
        )
        list_audio_devices()  # Show available devices for debugging

    return None


def create_blackhole_input_stream(callback, **kwargs):
    """Create an input stream using BlackHole device.

    Args:
        callback: Audio callback function
        **kwargs: Additional arguments for InputStream

    Returns:
        InputStream object or None if failed
    """
    blackhole_input = find_blackhole_device("input")
    if blackhole_input is None:
        return None

    try:
        return sd.InputStream(
            callback=callback,
            device=blackhole_input,
            dtype=kwargs.get("dtype", "int16"),
            channels=kwargs.get("channels", 1),
            samplerate=kwargs.get("samplerate", 24000),
            blocksize=kwargs.get("blocksize", 2400),
        )
    except Exception as e:
        logger.error(f"Failed to create BlackHole input stream: {e}")
        return None


def create_blackhole_output_stream(callback, **kwargs):
    """Create an output stream using BlackHole device.

    Args:
        callback: Audio callback function
        **kwargs: Additional arguments for OutputStream

    Returns:
        OutputStream object or None if failed
    """
    blackhole_output = find_blackhole_device("output")
    if blackhole_output is None:
        return None

    try:
        return sd.OutputStream(
            callback=callback,
            device=blackhole_output,
            dtype=kwargs.get("dtype", "int16"),
            channels=kwargs.get("channels", 1),
            samplerate=kwargs.get("samplerate", 24000),
            blocksize=kwargs.get("blocksize", 2400),
        )
    except Exception as e:
        logger.error(f"Failed to create BlackHole output stream: {e}")
        return None


def test_blackhole_devices() -> None:
    """Test BlackHole device selection and basic audio functionality."""
    logging.basicConfig(level=logging.INFO)

    print("Testing BlackHole device selection...")
    list_audio_devices()

    mic_id = set_mic_to_blackhole()
    speaker_id = set_speaker_to_blackhole()

    _test_microphone(mic_id)
    _test_speaker(speaker_id)


def _test_microphone(mic_id: Optional[int]) -> None:
    """Test microphone recording from BlackHole input."""
    if mic_id is None:
        print("❌ Failed to set microphone to BlackHole")
        return

    print(f"✅ Microphone set to BlackHole (Device ID: {mic_id})")

    try:
        duration = 1.0
        sample_rate = 24000

        recorded_audio = []

        def audio_callback(indata, frames_, time_, status):
            if status:
                print(f"Status: {status}")
            recorded_audio.extend(indata[:, 0])

        with sd.InputStream(
            device=mic_id,
            samplerate=sample_rate,
            channels=1,
            dtype="float32",
            callback=audio_callback,
        ):
            print("🎤 Recording 1 second of audio from BlackHole input...")
            time.sleep(duration)

        if recorded_audio:
            print(
                f"✅ Successfully recorded {len(recorded_audio)} samples from BlackHole input"
            )
        else:
            print("⚠️ No audio data received from BlackHole input")

    except Exception as e:
        print(f"⚠️ Could not record from BlackHole input: {e}")


def _test_speaker(speaker_id: Optional[int]) -> None:
    """Test speaker output through BlackHole."""
    if speaker_id is None:
        print("❌ Failed to set speaker to BlackHole")
        return

    print(f"✅ Speaker set to BlackHole (Device ID: {speaker_id})")

    import numpy as np

    try:
        duration = 1.0
        sample_rate = 24000
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        tone = np.sin(440 * 2 * np.pi * t) * 0.3

        with sd.OutputStream(
            device=speaker_id, samplerate=sample_rate, channels=1, dtype="float32"
        ) as stream:
            stream.write(tone.astype("float32"))
        print("🔊 Test tone played through BlackHole output")

    except Exception as e:
        print(f"⚠️ Could not play test tone: {e}")


if __name__ == "__main__":
    test_blackhole_devices()
