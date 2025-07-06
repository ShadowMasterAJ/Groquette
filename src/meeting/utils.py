"""Meeting utilities - Reusable functions for meeting automation."""

import os
import subprocess
import sys
import time
from typing import Optional

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from ..audio.audio_manager import AudioManager


def setup_chrome_driver() -> webdriver.Chrome:
    """Initialize Chrome driver with meeting-optimized settings."""
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


def login_to_google(driver: webdriver.Chrome, email: str, password: str) -> None:
    """Login to Google account."""
    driver.get(
        "https://accounts.google.com/ServiceLogin?hl=en&passive=true&continue=https://www.google.com/&ec=GAZAAQ"
    )
    driver.find_element(By.ID, "identifierId").send_keys(email)
    driver.find_element(By.ID, "identifierNext").click()
    time.sleep(2)

    driver.find_element(
        By.XPATH, '//*[@id="password"]/div[1]/div/div[1]/input'
    ).send_keys(password)
    driver.find_element(By.ID, "passwordNext").click()
    time.sleep(2)


def turn_off_microphone(driver: webdriver.Chrome) -> None:
    """Turn off microphone."""
    try:
        driver.find_element(
            By.CSS_SELECTOR, 'button[aria-label="Turn off microphone"]'
        ).click()
    except Exception as e:
        print(f"Could not turn off microphone: {e}")


def turn_on_microphone(driver) -> None:
    """Turn on microphone."""
    try:
        driver.find_element(
            By.CSS_SELECTOR, 'button[aria-label="Turn on microphone"]'
        ).click()
        print("🔊 Microphone turned on")
    except Exception as e:
        print(f"Could not turn on microphone: {e}")


def set_microphone_to_blackhole(driver: webdriver.Chrome) -> None:
    """Set microphone input to BlackHole."""
    try:
        mic_dropdown = driver.find_element(
            By.CSS_SELECTOR, 'button[aria-label*="Microphone"]'
        )
        mic_dropdown.click()
        blackhole_option = driver.find_element(
            By.XPATH,
            "//span[contains(text(), 'BlackHole 2ch (Virtual)')]//ancestor::li[@role='menuitemradio']",
        )
        driver.execute_script("arguments[0].click();", blackhole_option)
        print("✓ Successfully selected BlackHole input device")

    except Exception as e:
        print(f"Could not configure microphone to BlackHole: {e}")


def set_speaker_to_blackhole(driver: webdriver.Chrome) -> None:
    """Set speaker output to BlackHole with verification."""
    try:
        speaker_dropdown = driver.find_element(
            By.CSS_SELECTOR, 'button[aria-label*="Speaker"]'
        )
        speaker_dropdown.click()

        speaker_menu = driver.find_element(
            By.XPATH,
            "//*[@id='yDmH0d']/c-wiz/div/div/div[65]/div[3]/div/div[2]/div[4]/div/div/div[1]/div[2]/div/div/div[2]/div/span/span/div/div[2]/div",
        )
        blackhole_options = speaker_menu.find_elements(
            By.XPATH,
            ".//span[contains(text(), 'BlackHole 2ch (Virtual)')]//ancestor::li[@role='menuitemradio']",
        )
        if blackhole_options:
            blackhole_to_select = blackhole_options[0]
            driver.execute_script("arguments[0].click();", blackhole_to_select)
            time.sleep(1)
            speaker_label = speaker_dropdown.get_attribute("aria-label")

            if speaker_label and "BlackHole" in speaker_label:
                print("✓ Successfully selected BlackHole output device")
            else:
                print("❌ Could not select BlackHole output device")

    except Exception as e:
        print(f"Could not configure speaker to BlackHole: {e}")


def toggle_camera(driver: webdriver.Chrome) -> None:
    """Turn off camera."""
    try:
        driver.find_element(
            By.XPATH,
            '//*[@id="yDmH0d"]/c-wiz/div/div/div[65]/div[3]/div/div[2]/div[4]/div/div/div[1]/div[1]/div/div[7]/div[2]/div',
        ).click()
    except Exception as e:
        print(f"Could not turn off camera: {e}")


def start_voice_agent_process() -> Optional[subprocess.Popen[bytes]]:
    """Start the voice agent in a separate console process."""
    try:
        audio_manager = AudioManager()
        print("🤖 Starting voice agent console process...")

        current_dir = os.path.dirname(os.path.abspath(__file__))
        agent_script = os.path.join(current_dir, "..", "ai", "voice_agent.py")
        voice_agent_process = subprocess.Popen(
            [sys.executable, agent_script, "console"]
        )
        print("✅ Voice agent console process started")
        audio_manager.cleanup()
        return voice_agent_process

    except Exception as e:
        print(f"Failed to start voice agent: {e}")
        return None


def leave_meeting_cleanup(
    driver: webdriver.Chrome, voice_agent_process: Optional[subprocess.Popen[bytes]]
) -> None:
    """Leave meeting and cleanup resources."""
    # Stop voice agent process
    if voice_agent_process:
        try:
            voice_agent_process.terminate()
            voice_agent_process.wait(timeout=2)
        except Exception as e:
            print(f"⚠️ Error stopping voice agent: {e}")

    # Leave the meeting
    if driver:
        try:
            driver.find_element(
                By.CSS_SELECTOR, 'button[aria-label="Leave call"]'
            ).click()
        except Exception:
            pass

        driver.quit()
