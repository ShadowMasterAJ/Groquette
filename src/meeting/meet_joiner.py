"""Google Meet Joiner - Automated meeting joining"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
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
        time.sleep(3)
        
        self.driver.find_element(By.XPATH, '//*[@id="password"]/div[1]/div/div[1]/input').send_keys(self.password)
        self.driver.find_element(By.ID, "passwordNext").click()
        time.sleep(4)
    
    def _navigate_to_meeting(self):
        """Navigate to the meeting URL"""
        self.driver.get(self.meet_url)
        time.sleep(3)
    
    def _setup_meeting_preferences(self):
        """Turn off mic and camera before joining"""
        self._set_microphone_to_blackhole()
        self._turn_off_camera()
    
    def _set_microphone_to_blackhole(self):
        """Set microphone input to BlackHole"""
        try:
            # First, click on the microphone button to access settings
            mic_button = self.driver.find_element(By.CSS_SELECTOR, '[aria-label="Turn on microphone"]')
            mic_button.click()
            time.sleep(1)
            # TODO: Fix this, it's not working

            # Look for the microphone settings dropdown arrow or menu button
            try:
                # Try to find the dropdown arrow next to the microphone button
                mic_dropdown = self.driver.find_element(By.CSS_SELECTOR, '[aria-label="Audio settings"]')
                
                mic_dropdown.click()
                time.sleep(2)
                
                # Look for audio input device selection menu
                try:
                    # Find the audio input devices list or menu
                    audio_devices_menu = self.driver.find_element(By.CSS_SELECTOR, '[role="menu"], [role="listbox"]')
                    
                    # Look for BlackHole in the available audio input devices
                    blackhole_options = self.driver.find_elements(By.XPATH, "//div[contains(text(), 'BlackHole') or contains(text(), 'blackhole') or contains(text(), 'BlackHole 2ch') or contains(text(), 'BlackHole 16ch')]")
                    
                    if blackhole_options:
                        blackhole_options[0].click()
                        time.sleep(1)
                        print("Successfully set microphone input to BlackHole")
                    else:
                        print("BlackHole not found in audio devices list")
                        # Try alternative method - look for settings gear icon
                        try:
                            settings_gear = self.driver.find_element(By.CSS_SELECTOR, '[aria-label*="Settings"], [data-tooltip*="Settings"]')
                            settings_gear.click()
                            time.sleep(2)
                            
                            # Look for audio settings in the settings menu
                            audio_settings = self.driver.find_element(By.XPATH, "//div[contains(text(), 'Audio') or contains(text(), 'Microphone')]")
                            audio_settings.click()
                            time.sleep(1)
                            
                            # Now look for BlackHole in the expanded audio settings
                            blackhole_in_settings = self.driver.find_element(By.XPATH, "//div[contains(text(), 'BlackHole') or contains(text(), 'blackhole')]")
                            blackhole_in_settings.click()
                            time.sleep(1)
                            print("Set microphone input to BlackHole via settings menu")
                            
                        except Exception as settings_e:
                            print(f"Could not access audio settings: {settings_e}")
                            # Final fallback - just turn off microphone
                            mic_button.click()
                            print("Fallback: Turned off microphone instead")
                        
                except Exception as menu_e:
                    print(f"Could not find audio devices menu: {menu_e}")
                    # Try clicking on the three dots menu for more options
                    try:
                        more_options = self.driver.find_element(By.CSS_SELECTOR, '[aria-label*="More options"], [aria-label*="More"]')
                        more_options.click()
                        time.sleep(1)
                        
                        # Look for audio or microphone settings in more options
                        audio_option = self.driver.find_element(By.XPATH, "//div[contains(text(), 'Audio') or contains(text(), 'Microphone') or contains(text(), 'Settings')]")
                        audio_option.click()
                        time.sleep(2)
                        
                        # Look for BlackHole in the expanded options
                        blackhole_option = self.driver.find_element(By.XPATH, "//div[contains(text(), 'BlackHole') or contains(text(), 'blackhole')]")
                        blackhole_option.click()
                        time.sleep(1)
                        print("Set microphone input to BlackHole via more options menu")
                        
                    except Exception as options_e:
                        print(f"Could not find BlackHole in more options: {options_e}")
                        # Final fallback
                        mic_button.click()
                        print("Fallback: Turned off microphone")
                
            except Exception as dropdown_e:
                print(f"Could not find microphone dropdown: {dropdown_e}")
                # Try right-clicking on microphone button for context menu
                try:
                    from selenium.webdriver.common.action_chains import ActionChains
                    actions = ActionChains(self.driver)
                    actions.context_click(mic_button).perform()
                    time.sleep(1)
                    
                    # Look for audio device options in context menu
                    blackhole_context = self.driver.find_element(By.XPATH, "//div[contains(text(), 'BlackHole') or contains(text(), 'blackhole')]")
                    blackhole_context.click()
                    time.sleep(1)
                    print("Set microphone input to BlackHole via context menu")
                    
                except Exception as context_e:
                    print(f"Context menu approach failed: {context_e}")
                    # Final fallback - turn off microphone
                    mic_button.click()
                    print("Fallback: Turned off microphone")
                
        except Exception as e:
            print(f"Could not configure microphone to BlackHole: {e}")
    
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
