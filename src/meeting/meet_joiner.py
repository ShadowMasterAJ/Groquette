"""Google Meet Joiner - Automated meeting joining."""

import subprocess
import time
from typing import Optional

from selenium.webdriver.common.by import By

from .utils import (
    leave_meeting_cleanup,
    login_to_google,
    set_microphone_to_blackhole,
    set_speaker_to_blackhole,
    setup_chrome_driver,
    start_voice_agent_process,
    toggle_camera,
)


class MeetJoiner:
    """Google Meet Joiner - Automated meeting joining."""

    def __init__(self, meet_url: str) -> None:
        """Initialize the meet joiner."""
        self.email = "groquette1"
        self.password = "groquette123456"
        self.meet_url = meet_url
        self.driver = setup_chrome_driver()
        self.voice_agent_process: Optional[subprocess.Popen[bytes]] = None

    def join_meeting(self) -> None:
        """Complete process to join a Google Meet."""
        print(f"Joining meeting: {self.meet_url}")

        login_to_google(self.driver, self.email, self.password)
        self._navigate_to_meeting()
        self._setup_meeting_preferences()
        self._join_meeting()

        # Start voice agent after successful join
        self.voice_agent_process = start_voice_agent_process()

    def _navigate_to_meeting(self) -> None:
        """Navigate to the meeting URL."""
        self.driver.get(self.meet_url)
        time.sleep(1)

    def _setup_meeting_preferences(self) -> None:
        """Configure audio settings and turn off camera before joining."""
        toggle_camera(self.driver)
        set_microphone_to_blackhole(self.driver)
        set_speaker_to_blackhole(self.driver)

    def _join_meeting(self) -> None:
        """Click the join meeting button and wait if meeting is closed."""
        try:
            # Click the join meeting button
            self.driver.find_element(
                By.XPATH,
                '//*[@id="yDmH0d"]/c-wiz/div/div/div[65]/div[3]/div/div[2]/div[4]/div/div/div[2]/div[1]/div[2]/div[2]/div/div',
            ).click()

            time.sleep(2)

            # Check if we successfully joined by looking for leave call button
            try:
                self.driver.find_element(
                    By.CSS_SELECTOR, 'button[aria-label="Leave call"]'
                )
                print("✓ Successfully joined the meeting!")
                return
            except BaseException:
                pass

            # If not in meeting, we might need to wait to be let in
            print("⏳ Waiting to be let into the meeting...")

            # Wait up to 5 minutes to be let in
            max_wait_time = 300
            wait_interval = 5
            elapsed_time = 0

            while elapsed_time < max_wait_time:
                time.sleep(wait_interval)
                elapsed_time += wait_interval

                # Check if we've been let in
                try:
                    self.driver.find_element(
                        By.CSS_SELECTOR, 'button[aria-label="Leave call"]'
                    )
                    print("✓ Successfully let into the meeting!")
                    return
                except BaseException:
                    print(f"Still waiting... ({elapsed_time}s elapsed)")

            print("⚠️ Timeout waiting to be let into the meeting")

        except Exception as e:
            print(f"Failed to join: {e}")
            raise

    def leave_meeting(self) -> None:
        """Leave meeting and cleanup."""
        leave_meeting_cleanup(self.driver, self.voice_agent_process)
