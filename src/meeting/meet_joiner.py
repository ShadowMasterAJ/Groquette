"""Google Meet Joiner - Automated meeting joining."""

import os
import subprocess
import sys
import time
from typing import Optional

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from ..audio.audio_manager import AudioManager


class MeetJoiner:
    """Google Meet Joiner - Automated meeting joining."""

    def __init__(self, meet_url: str) -> None:
        """Initialize the meet joiner."""
        self.email = "groquette1"
        self.password = "groquette123456"
        self.meet_url = meet_url
        self.driver = self._setup_driver()
        self.voice_agent_process: Optional[subprocess.Popen[bytes]] = None

    def _setup_driver(self) -> webdriver.Chrome:
        """Initialize Chrome driver."""
        opt = Options()
        opt.add_argument("--disable-blink-features=AutomationControlled")
        opt.add_argument("--start-maximized")
        opt.add_experimental_option(
            "prefs",
            {
                "profile.default_content_setting_values.media_stream_mic": 1,
                "profile.default_content_setting_values.media_stream_camera": 1,
                "profile.default_content_setting_values.notifications": 1,
            },
        )
        return webdriver.Chrome(options=opt)

    def join_meeting(self) -> None:
        """Complete process to join a Google Meet."""
        print(f"Joining meeting: {self.meet_url}")

        self._login_to_google()
        self._navigate_to_meeting()
        self._setup_meeting_preferences()
        self._join_meeting()

        # Start voice agent after successful join
        self._start_voice_agent()

    def _login_to_google(self) -> None:
        """Login to Google account."""
        self.driver.get(
            "https://accounts.google.com/ServiceLogin?hl=en&passive=true&continue=https://www.google.com/&ec=GAZAAQ"
        )
        self.driver.find_element(By.ID, "identifierId").send_keys(self.email)
        self.driver.find_element(By.ID, "identifierNext").click()
        time.sleep(2)

        self.driver.find_element(
            By.XPATH, '//*[@id="password"]/div[1]/div/div[1]/input'
        ).send_keys(self.password)
        self.driver.find_element(By.ID, "passwordNext").click()
        time.sleep(2)

    def _navigate_to_meeting(self) -> None:
        """Navigate to the meeting URL."""
        self.driver.get(self.meet_url)
        time.sleep(1)

    def _setup_meeting_preferences(self) -> None:
        """Configure audio settings and turn off camera before joining."""
        self._toggle_camera()
        self._set_microphone_to_blackhole()
        self._set_speaker_to_blackhole()

    def _turn_off_microphone(self) -> None:
        """Turn off microphone."""
        try:
            self.driver.find_element(
                By.CSS_SELECTOR, 'button[aria-label="Turn off microphone"]'
            ).click()
        except Exception as e:
            print(f"Could not turn off microphone: {e}")

    def _set_microphone_to_blackhole(self) -> None:
        """Set microphone input to BlackHole."""
        try:
            mic_dropdown = self.driver.find_element(
                By.CSS_SELECTOR, 'button[aria-label*="Microphone"]'
            )
            mic_dropdown.click()
            blackhole_option = self.driver.find_element(
                By.XPATH,
                "//span[contains(text(), 'BlackHole 2ch (Virtual)')]//ancestor::li[@role='menuitemradio']",
            )
            self.driver.execute_script("arguments[0].click();", blackhole_option)
            print("✓ Successfully selected BlackHole input device")

        except Exception as e:
            print(f"Could not configure microphone to BlackHole: {e}")

    def _set_speaker_to_blackhole(self) -> None:
        """Set speaker output to BlackHole with verification."""
        try:
            speaker_dropdown = self.driver.find_element(
                By.CSS_SELECTOR, 'button[aria-label*="Speaker"]'
            )
            speaker_dropdown.click()

            speaker_menu = self.driver.find_element(
                By.XPATH,
                "//*[@id='yDmH0d']/c-wiz/div/div/div[65]/div[3]/div/div[2]/div[4]/div/div/div[1]/div[2]/div/div/div[2]/div/span/span/div/div[2]/div",
            )
            blackhole_options = speaker_menu.find_elements(
                By.XPATH,
                ".//span[contains(text(), 'BlackHole 2ch (Virtual)')]//ancestor::li[@role='menuitemradio']",
            )
            if blackhole_options:
                blackhole_to_select = blackhole_options[0]
                self.driver.execute_script("arguments[0].click();", blackhole_to_select)
                time.sleep(1)
                speaker_label = speaker_dropdown.get_attribute("aria-label")

                if speaker_label and "BlackHole" in speaker_label:
                    print("✓ Successfully selected BlackHole output device")
                else:
                    print("❌ Could not select BlackHole output device")

        except Exception as e:
            print(f"Could not configure speaker to BlackHole: {e}")

    def _toggle_camera(self) -> None:
        """Turn off camera."""
        try:
            self.driver.find_element(
                By.XPATH,
                '//*[@id="yDmH0d"]/c-wiz/div/div/div[65]/div[3]/div/div[2]/div[4]/div/div/div[1]/div[1]/div/div[7]/div[2]/div',
            ).click()
        except Exception as e:
            print(f"Could not turn off camera: {e}")

    def _join_meeting(self) -> None:
        """Click the join meeting button."""
        try:
            self.driver.find_element(
                By.XPATH,
                '//*[@id="yDmH0d"]/c-wiz/div/div/div[65]/div[3]/div/div[2]/div[4]/div/div/div[2]/div[1]/div[2]/div[2]/div/div',
            ).click()
            print("✓ Successfully joined the meeting!")
        except Exception as e:
            print(f"Failed to join: {e}")
            raise

    def _start_voice_agent(self) -> None:
        """Start the voice agent in a separate console process."""
        try:
            audio_manager = AudioManager()
            print("🤖 Starting voice agent console process...")

            current_dir = os.path.dirname(os.path.abspath(__file__))
            agent_script = os.path.join(current_dir, "..", "ai", "voice_agent.py")
            self.voice_agent_process = subprocess.Popen(
                [sys.executable, agent_script, "console"]
            )
            print("✅ Voice agent console process started")
            audio_manager.cleanup()

        except Exception as e:
            print(f"Failed to start voice agent: {e}")

    def leave_meeting(self) -> None:
        """Leave meeting and cleanup."""
        # Stop voice agent process
        if self.voice_agent_process:
            try:
                self.voice_agent_process.terminate()
                self.voice_agent_process.wait(timeout=2)
            except Exception as e:
                print(f"⚠️ Error stopping voice agent: {e}")

        # Leave the meeting
        if self.driver:
            try:
                self.driver.find_element(
                    By.CSS_SELECTOR, 'button[aria-label="Leave call"]'
                ).click()
            except Exception:
                pass

            self.driver.quit()
