"""Google Meet Joiner - Automated meeting joining."""

import os
import subprocess
import threading
import time
from typing import Optional

from dotenv import load_dotenv
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .ipc_commands import IPCCommands
from .utils import (
    focus_chrome_window,
    leave_meeting_cleanup,
    login_to_google,
    set_microphone_to_blackhole,
    set_speaker_to_blackhole,
    setup_chrome_driver,
    start_voice_agent_process,
    toggle_camera,
    turn_off_microphone,
    turn_on_microphone,
)

load_dotenv()


class MeetJoiner:
    """Google Meet Joiner - Automated meeting joining."""

    def __init__(self, meet_url: str) -> None:
        """Initialize the meet joiner."""
        self.email = os.getenv("GOOGLE_EMAIL")
        self.password = os.getenv("GOOGLE_PASSWORD")
        self.meet_url = meet_url
        self.driver = setup_chrome_driver()
        self.voice_agent_process: Optional[subprocess.Popen[bytes]] = None
        self.ipc = IPCCommands()
        self.is_running = True

    def join_meeting(self) -> None:
        """Complete process to join a Google Meet."""
        print(f"Joining meeting: {self.meet_url}")

        login_to_google(self.driver, self.email, self.password)
        self._navigate_to_meeting()
        self._setup_meeting_preferences()
        self._join_meeting()

        # Start voice agent after successful join
        self.voice_agent_process = start_voice_agent_process()

        # Start IPC command handler in a separate thread
        self.ipc_thread = threading.Thread(target=self.handle_ipc_commands, daemon=True)
        self.ipc_thread.start()
        print("🔄 IPC command handler started")

    def _navigate_to_meeting(self) -> None:
        """Navigate to the meeting URL."""
        self.driver.get(self.meet_url)
        time.sleep(1)

    def _setup_meeting_preferences(self) -> None:
        """Configure audio settings and turn off camera before joining."""
        toggle_camera(self.driver)
        time.sleep(1)
        set_microphone_to_blackhole(self.driver)
        set_speaker_to_blackhole(self.driver)

    def _join_meeting(self) -> None:
        """Click the join meeting button and wait if meeting is closed."""
        # Wait for page to stabilize
        time.sleep(1)

        # Find and click the join button
        join_button, button_text = self._find_join_button()
        self._click_button(join_button, button_text)

        # Check if we successfully joined
        if self._check_if_joined():
            print("✅ Successfully joined the meeting!")
            return

        # Handle waiting to be let in
        if button_text and "Ask to join" in button_text:
            self._wait_for_ask_to_join_approval()
        else:
            self._wait_for_join_approval()

    def _find_join_button(self):
        """Find the join or ask to join button."""
        focus_chrome_window(self.driver)
        js_code = """
        // First try specific class buttons
        const buttons = document.querySelectorAll('button.UywwFc-LgbsSe');
        for (let btn of buttons) {
            const span = btn.querySelector('span.UywwFc-vQzf8d');
            if (span && (span.textContent.includes('Join now') || span.textContent.includes('Ask to join'))) {
                return btn;
            }
        }

        // Fallback: check all buttons for text
        const allButtons = document.querySelectorAll('button');
        for (let btn of allButtons) {
            if (btn.textContent.includes('Join now') || btn.textContent.includes('Ask to join')) {
                return btn;
            }
        }

        return null;
        """

        try:
            join_button = self.driver.execute_script(js_code)
            if not join_button:
                raise Exception("Could not find join button")

            button_text = join_button.text
            print(f"🔍 Found '{button_text}' button")
            return join_button, button_text
        except Exception as e:
            raise Exception(f"Failed to find join button: {e}")

    def _click_button(self, button, button_text):
        """Click the button with fallback to JavaScript click."""
        try:
            button.click()
            print(f"✓ Clicked '{button_text}' button")
        except ElementClickInterceptedException:
            # Fallback to JavaScript click if regular click is intercepted
            self.driver.execute_script("arguments[0].click();", button)
            print(f"✓ Clicked '{button_text}' button using JavaScript")

    def _check_if_joined(self):
        """Check if we successfully joined the meeting."""
        try:
            wait = WebDriverWait(self.driver, 10)
            wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'button[aria-label="Leave call"]')
                )
            )
            return True
        except TimeoutException:
            return False

    def _wait_for_ask_to_join_approval(self):
        """Wait to be let in after clicking 'Ask to join'."""
        print("⏳ Asked to join. Waiting to be let into the meeting...")

        max_wait_time = 300
        wait_interval = 3
        elapsed_time = 0

        while elapsed_time < max_wait_time:
            time.sleep(wait_interval)
            elapsed_time += wait_interval

            # Check if we've been let in
            if self._is_in_meeting():
                print("✅ Successfully let into the meeting!")
                return

            # Try clicking Ask to join again if needed
            self._retry_ask_to_join()
            print(f"⏳ Still waiting... ({elapsed_time}s elapsed)")

        print("⚠️ Timeout waiting to be let into the meeting")

    def _wait_for_join_approval(self):
        """Wait briefly for 'Join now' approval."""
        print("⏳ Waiting to be let into the meeting...")
        time.sleep(5)

        # Final check
        if self._is_in_meeting():
            print("✅ Successfully joined the meeting!")
        else:
            print("⚠️ Could not confirm meeting join")

    def _is_in_meeting(self):
        """Check if we are in the meeting."""
        try:
            self.driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Leave call"]')
            return True
        except Exception:
            return False

    def _retry_ask_to_join(self):
        """Check and click 'Ask to join' button again if present."""
        try:
            js_check = """
            const buttons = document.querySelectorAll('button');
            for (let btn of buttons) {
                if (btn.textContent.includes('Ask to join')) {
                    return btn;
                }
            }
            return null;
            """
            ask_again_button = self.driver.execute_script(js_check)
            if ask_again_button:
                self.driver.execute_script("arguments[0].click();", ask_again_button)
                print("🔄 Clicked 'Ask to join' again")
        except Exception:
            pass

    def handle_ipc_commands(self) -> None:
        """Check and handle IPC commands from voice agent."""
        while self.is_running:
            try:
                # Check for command
                cmd_data = self.ipc.check_for_command()
                if cmd_data:
                    command = cmd_data.get("command")
                    result = "Unknown command"

                    # Handle different commands
                    if command == "mute_microphone":
                        turn_off_microphone(self.driver)
                        result = "Microphone muted"
                    elif command == "unmute_microphone":
                        turn_on_microphone(self.driver)
                        result = "Microphone unmuted"
                    elif command == "check_microphone_status":
                        # Check current microphone status
                        try:
                            focus_chrome_window(self.driver)
                            mic_button = self.driver.find_element(
                                By.CSS_SELECTOR, 'button[aria-label*="microphone"]'
                            )
                            aria_label = mic_button.get_attribute("aria-label")
                            if "Turn off" in aria_label:
                                result = "Microphone is currently unmuted"
                            else:
                                result = "Microphone is currently muted"
                        except Exception:
                            result = "Could not check microphone status"
                    elif command == "leave_meeting":
                        self.leave_meeting()
                        result = "Left the meeting"
                        self.is_running = False

                    # Send response
                    self.ipc.send_response(result)

                time.sleep(0.1)  # Check every 100ms

            except KeyboardInterrupt:
                print("\n🛑 Stopping IPC handler")
                break
            except Exception as e:
                print(f"Error in IPC handler: {e}")
                time.sleep(1)

    def leave_meeting(self) -> None:
        """Leave meeting and cleanup."""
        self.is_running = False
        leave_meeting_cleanup(self.driver, self.voice_agent_process)
