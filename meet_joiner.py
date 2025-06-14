# import required modules
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import sys


def Glogin(mail_address, password,meetLink):
    # Login Page
    driver.get(
        'https://accounts.google.com/ServiceLogin?hl=en&passive=true&continue=https://www.google.com/&ec=GAZAAQ')

    # input Gmail
    driver.find_element(By.ID, "identifierId").send_keys(mail_address)
    driver.find_element(By.ID, "identifierNext").click()
    driver.implicitly_wait(10)

    # input Password
    driver.find_element(By.XPATH,
        '//*[@id="password"]/div[1]/div/div[1]/input').send_keys(password)
    driver.implicitly_wait(10)
    driver.find_element(By.ID, "passwordNext").click()
    time.sleep(4)
    # go to google home page
    driver.get(meetLink)
    driver.implicitly_wait(100)

def turnOffMicCam():
    # turn off Microphone
    time.sleep(2)
    driver.find_element(By.XPATH,
        '//*[@id="yDmH0d"]/c-wiz/div/div/div[65]/div[3]/div/div[2]/div[4]/div/div/div[1]/div[1]/div/div[7]/div[1]/div').click()
    driver.implicitly_wait(3000)

    # turn off camera
    time.sleep(1)
    driver.find_element(By.XPATH,
        '//*[@id="yDmH0d"]/c-wiz/div/div/div[65]/div[3]/div/div[2]/div[4]/div/div/div[1]/div[1]/div/div[7]/div[2]/div').click()
    driver.implicitly_wait(3000)


def joinNow():
    # Join meet
    time.sleep(1)
    driver.implicitly_wait(4)
    
    print("Attempting to click join button...")
    try:
        driver.find_element(By.XPATH,
            '//*[@id="yDmH0d"]/c-wiz/div/div/div[65]/div[3]/div/div[2]/div[4]/div/div/div[2]/div[1]/div[2]/div[2]/div/div').click()
        print("Successfully clicked join button")
    except Exception as e:
        print(f"Failed to click join button: {str(e)}")

def leave_call():
    # Leave the meeting
    driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Leave call"]').click()
    driver.quit()
    
if __name__ == "__main__":
    # Get meetLink from command line arguments
    if len(sys.argv) > 1:
        # Check if the provided link matches the expected format
        # Check if the code matches xxx-xxxx-xxx format using string length and hyphens
        code = sys.argv[1]
        parts = code.split('-')
        if len(parts) != 3 or len(parts[0]) != 3 or len(parts[1]) != 4 or len(parts[2]) != 3:
            print("Invalid meeting code format. Expected format: xxx-xxxx-xxx")
            sys.exit(1)
        meetLink = f"https://meet.google.com/{sys.argv[1]}"
    else:
        print("Please provide the Meet link as a command-line argument.")
        sys.exit(1)

    # assign email id and password
    mail_address = 'groquette1'
    password = 'groquette123456'

    # create chrome instance
    opt = Options()
    opt.add_argument('--disable-blink-features=AutomationControlled')
    opt.add_argument('--start-maximized')
    opt.add_experimental_option("prefs", {
        "profile.default_content_setting_values.media_stream_mic": 1,
        "profile.default_content_setting_values.media_stream_camera": 1,
        "profile.default_content_setting_values.geolocation": 0,
        "profile.default_content_setting_values.notifications": 1
    })
    driver = webdriver.Chrome(options=opt)

    
    # # login to Google account
    Glogin(mail_address, password,meetLink)

    turnOffMicCam()
    joinNow()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        leave_call()
