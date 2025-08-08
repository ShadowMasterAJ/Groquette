"""Inter-process communication for voice agent to control meeting UI."""

import json
import os
import time
from pathlib import Path
from typing import Dict, Optional


class IPCCommands:
    """Simple file-based IPC for voice agent to send commands to Selenium process."""

    def __init__(self):
        """Initialize IPC with a command file in temp directory."""
        self.command_file = Path("/tmp/groquette_commands.json")
        self.response_file = Path("/tmp/groquette_responses.json")
        self._clear_files()

    def _clear_files(self):
        """Clear command and response files."""
        if self.command_file.exists():
            self.command_file.unlink()
        if self.response_file.exists():
            self.response_file.unlink()

    def send_command(self, command: str, params: Optional[Dict] = None) -> str:
        """Send a command from voice agent to Selenium process."""
        cmd_data = {
            "command": command,
            "params": params or {},
            "timestamp": time.time(),
        }

        # Write command
        with open(self.command_file, "w") as f:
            json.dump(cmd_data, f)

        # Wait for response (max 5 seconds)
        start_time = time.time()
        while time.time() - start_time < 5:
            if self.response_file.exists():
                try:
                    with open(self.response_file, "r") as f:
                        response = json.load(f)

                    # Clean up response file
                    self.response_file.unlink()

                    return response.get("result", "Command executed")
                except Exception:
                    pass

            time.sleep(0.1)

        return "Command sent but no response received"

    def check_for_command(self) -> Optional[Dict]:
        """Check for pending command from voice agent (used by Selenium process)."""
        if not self.command_file.exists():
            return None

        try:
            with open(self.command_file, "r") as f:
                cmd_data = json.load(f)

            # Clean up command file
            self.command_file.unlink()

            return cmd_data
        except Exception:
            return None

    def send_response(self, result: str):
        """Send response back to voice agent (used by Selenium process)."""
        response_data = {"result": result, "timestamp": time.time()}

        with open(self.response_file, "w") as f:
            json.dump(response_data, f)
