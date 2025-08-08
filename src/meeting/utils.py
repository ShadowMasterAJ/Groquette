"""Meeting utilities - Reusable functions for meeting automation."""

import os
import subprocess
import sys
import time
from typing import Optional

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


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


def focus_chrome_window(driver: webdriver.Chrome) -> None:
    """Focus the Chrome browser window to bring it to foreground."""
    try:
        driver.switch_to.window(driver.current_window_handle)
        driver.execute_script("window.focus();")
    except Exception as e:
        print(f"Could not focus Chrome window: {e}")


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


def toggle_camera(driver: webdriver.Chrome) -> None:
    """Turn off camera."""
    try:
        focus_chrome_window(driver)
        camera_button = driver.find_element(
            By.CSS_SELECTOR, '[role="button"][aria-label="Turn off camera"]'
        )

        camera_button.click()
    except Exception as e:
        print(f"Could not turn off camera: {e}")


def turn_off_microphone(driver: webdriver.Chrome) -> None:
    """Turn off microphone."""
    try:
        focus_chrome_window(driver)
        driver.find_element(
            By.CSS_SELECTOR, 'button[aria-label="Turn off microphone"]'
        ).click()
    except Exception as e:
        print(f"Could not turn off microphone: {e}")


def turn_on_microphone(driver) -> None:
    """Turn on microphone."""
    try:
        focus_chrome_window(driver)
        driver.find_element(
            By.CSS_SELECTOR, 'button[aria-label="Turn on microphone"]'
        ).click()
        print("🔊 Microphone turned on")
    except Exception as e:
        print(f"Could not turn on microphone: {e}")


def set_microphone_to_blackhole(driver: webdriver.Chrome) -> None:
    """Set microphone input to BlackHole."""
    try:
        focus_chrome_window(driver)
        mic_dropdown = driver.find_element(
            By.CSS_SELECTOR, 'button[aria-label*="Microphone"][aria-haspopup="menu"]'
        )
        print(
            f"🔍 Found microphone dropdown: {mic_dropdown.get_attribute('aria-label')}"
        )

        mic_dropdown.click()
        print("🖱️ Clicked microphone dropdown")

        blackhole_option = driver.find_element(
            By.XPATH,
            "//span[contains(text(), 'BlackHole 2ch (Virtual)')]//ancestor::li[@role='menuitemradio']",
        )
        print(f"🔍 Found BlackHole option: {blackhole_option.text}")

        driver.execute_script("arguments[0].click();", blackhole_option)
        print("✅ Successfully selected BlackHole input device")

    except Exception as e:
        print(f"Could not configure microphone to BlackHole: {e}")


def set_speaker_to_blackhole(driver: webdriver.Chrome) -> None:
    """Set speaker output to BlackHole with direct index selection."""
    try:
        focus_chrome_window(driver)
        print("🔍 Setting speaker to BlackHole...")

        # Open the speaker dropdown
        speaker_dropdown = driver.find_element(
            By.CSS_SELECTOR, 'button[aria-label*="Speaker"][aria-haspopup="menu"]'
        )
        current_label = speaker_dropdown.get_attribute("aria-label")
        print(f"  Current speaker: {current_label}")

        # Check if already set to BlackHole
        if "BlackHole" in current_label:
            print("  ✅ Speaker already set to BlackHole")
            return

        speaker_dropdown.click()
        time.sleep(0.5)

        # Find BlackHole option by looking through menu items
        menu_items = driver.find_elements(By.CSS_SELECTOR, 'li[role="menuitemradio"]')
        blackhole_found = False

        for idx, item in enumerate(menu_items):
            if "BlackHole" in item.text:
                print(f"  Found BlackHole at index {idx}: {item.text}")
                # Force click the item
                driver.execute_script("arguments[0].click();", item)
                print("  ✅ Clicked BlackHole option")
                blackhole_found = True
                break

        if not blackhole_found:
            print("  ❌ BlackHole option not found in menu")
            # Close menu
            driver.find_element(By.TAG_NAME, "body").click()
            return

        # Wait for change to take effect
        time.sleep(0.5)

        # Verify the selection
        selected_label = driver.find_element(
            By.CSS_SELECTOR, 'button[aria-label*="Speaker"][aria-haspopup="menu"]'
        ).get_attribute("aria-label")

        if "BlackHole" in selected_label:
            print(f"  ✅ Speaker successfully set to: {selected_label}")
        else:
            print(f"  ⚠️ Speaker label not updated: {selected_label}")
            print("  ⚠️ Audio may still route through BlackHole despite the label")

    except Exception as e:
        print(f"❌ Could not configure speaker to BlackHole: {e}")
        import traceback

        traceback.print_exc()


def start_voice_agent_process() -> Optional[subprocess.Popen[bytes]]:
    """Start the voice agent in a separate console process."""
    try:
        print("🤖 Starting voice agent console process...")

        current_dir = os.path.dirname(os.path.abspath(__file__))
        agent_script = os.path.join(current_dir, "..", "ai", "voice_agent.py")
        project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
        voice_agent_process = subprocess.Popen(
            [sys.executable, agent_script, "console"], cwd=project_root
        )
        print("✅ Voice agent console process started")
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
