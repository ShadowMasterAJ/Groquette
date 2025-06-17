"""Google Meet Joiner - Automated meeting joining"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import time


class MeetJoiner:
    def __init__(self, meet_url):
        self.email = 'groquette1'
        self.password = 'groquette123456'
        self.meet_url = meet_url
        self.driver = self._setup_driver()
    
    def _setup_driver(self):
        """Initialize Chrome driver"""
        opt = Options()
        opt.add_argument('--disable-blink-features=AutomationControlled')
        opt.add_argument('--start-maximized')
        opt.add_experimental_option("prefs", {
            "profile.default_content_setting_values.media_stream_mic": 1,
            "profile.default_content_setting_values.media_stream_camera": 1,
            "profile.default_content_setting_values.notifications": 1
        })
        return webdriver.Chrome(options=opt)
    
    def join_meeting(self):
        """Complete process to join a Google Meet"""
        print(f"Joining meeting: {self.meet_url}")
        
        self._login_to_google()
        self._navigate_to_meeting()
        self._setup_meeting_preferences()
        self._join_meeting()
    
    def _login_to_google(self):
        """Login to Google account"""
        self.driver.get('https://accounts.google.com/ServiceLogin?hl=en&passive=true&continue=https://www.google.com/&ec=GAZAAQ')
        self.driver.find_element(By.ID, "identifierId").send_keys(self.email)
        self.driver.find_element(By.ID, "identifierNext").click()
        time.sleep(2)
        
        self.driver.find_element(By.XPATH, '//*[@id="password"]/div[1]/div/div[1]/input').send_keys(self.password)
        self.driver.find_element(By.ID, "passwordNext").click()
        time.sleep(2)
    
    def _navigate_to_meeting(self):
        """Navigate to the meeting URL"""
        self.driver.get(self.meet_url)
        time.sleep(2)
    
    def _setup_meeting_preferences(self):
        """Turn off mic and camera before joining"""
        self._set_microphone_to_blackhole()
        self._turn_off_camera()
    
    def _set_microphone_to_blackhole(self):
        """Set microphone input to BlackHole"""
        try:
            mic_button = self._click_microphone_button()
            if not mic_button:
                return
            
            self._click_audio_settings()
            self._select_blackhole_microphone()
                
        except Exception as e:
            print(f"Could not configure microphone to BlackHole: {e}")

    def _click_microphone_button(self):
        """Click the microphone button to access settings"""
        try:
            mic_button = self.driver.find_element(By.CSS_SELECTOR, '[aria-label="Turn off microphone"]')
            mic_button.click()
            time.sleep(1)
            return mic_button
        except Exception as e:
            print(f"Could not find microphone button: {e}")
            return None

    def _click_audio_settings(self):
        """Click the audio settings dropdown"""
        try:
            # Try multiple selectors for the audio settings button
            selectors = [
                'button[jsname="ndfw3d"][aria-label="Audio settings"]',
                '[aria-label="Audio settings"]',
                'button[aria-label*="Audio"]',
                'button[aria-label*="Microphone"]',
                'button[jsname="ndfw3d"]'
            ]
            
            for selector in selectors:
                try:
                    mic_dropdown = self.driver.find_element(By.CSS_SELECTOR, selector)
                    mic_dropdown.click()
                    time.sleep(1)
                    print(f"Successfully clicked audio settings button with selector: {selector}")
                    return
                except Exception as e:
                    print(f"Failed with selector {selector}: {e}")
                    continue
                    
            print("Could not find audio settings button with any selector")
        except Exception as e:
            print(f"Could not find audio settings button: {e}")
    
    def _select_blackhole_microphone(self):
        """Select BlackHole microphone from the dropdown menu"""
        try:
            # Wait a bit for the dropdown to fully load
            print("Waiting for dropdown to load...")
            time.sleep(2)
            
            # Find BlackHole by text content with JavaScript click
            print("Finding BlackHole by text content...")
            try:
                blackhole_option = self.driver.find_element(
                    By.XPATH, 
                    "//span[contains(text(), 'BlackHole 2ch (Virtual)')]//ancestor::li[@role='menuitemradio']"
                )
                print("Found BlackHole option by text content, clicking with JavaScript...")
                self.driver.execute_script("arguments[0].click();", blackhole_option)
                print("Successfully selected BlackHole microphone by text content")
                return
            except Exception as e:
                print(f"Failed to select BlackHole microphone: {e}")
                
            print("Could not find BlackHole microphone option")
            
        except Exception as e:
            print(f"Error selecting BlackHole microphone: {e}")
    
    def _turn_off_camera(self):
        """Turn off camera"""
        try:
            self.driver.find_element(By.XPATH, '//*[@id="yDmH0d"]/c-wiz/div/div/div[65]/div[3]/div/div[2]/div[4]/div/div/div[1]/div[1]/div/div[7]/div[2]/div').click()
        except Exception as e:
            print(f"Could not turn off camera: {e}")
    
    def _join_meeting(self):
        """Click the join meeting button"""
        time.sleep(2)
        try:
            self.driver.find_element(By.XPATH, '//*[@id="yDmH0d"]/c-wiz/div/div/div[65]/div[3]/div/div[2]/div[4]/div/div/div[2]/div[1]/div[2]/div[2]/div/div').click()
            print("Successfully joined the meeting!")
        except Exception as e:
            print(f"Failed to join: {e}")
            raise

    def keep_alive(self):
        """Keep session alive until interrupted"""
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            raise

    def leave_meeting(self):
        """Leave meeting and cleanup"""
        if self.driver:
            try:
                self.driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Leave call"]').click()
                time.sleep(1)
            except:
                pass
            finally:
                self.driver.quit()
                print("Left meeting and closed browser")

    def __del__(self):
        """Cleanup"""
        if hasattr(self, 'driver') and self.driver:
            try:
                self.driver.quit()
            except:
                pass
