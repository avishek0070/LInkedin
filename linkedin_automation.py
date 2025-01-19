import os
import time
import random
import logging

from dotenv import load_dotenv

# Selenium imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# 1. Load environment variables from .env file
load_dotenv()
LINKEDIN_EMAIL = os.getenv("LINKEDIN_EMAIL")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")

if not LINKEDIN_EMAIL or not LINKEDIN_PASSWORD:
    print("Error: Missing environment variables. Check your .env file for LINKEDIN_EMAIL and LINKEDIN_PASSWORD.")
    exit()

# 2. Configure logging
logging.basicConfig(
    level=logging.INFO,
    filename="linkedin_automation.log",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# 3. Set up the Chrome driver (incognito, non-headless)
chrome_options = Options()
chrome_options.add_argument("--incognito")
# If you'd like headless, uncomment below:
# chrome_options.add_argument("--headless")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=chrome_options
)

try:
    # 4. Open LinkedIn login page
    driver.get("https://www.linkedin.com/login")
    time.sleep(2)

    # 5. Enter credentials and log in
    try:
        username_input = driver.find_element(By.ID, "username")
        password_input = driver.find_element(By.ID, "password")
        username_input.send_keys(LINKEDIN_EMAIL)
        password_input.send_keys(LINKEDIN_PASSWORD)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
    except NoSuchElementException as e:
        print("Failed to locate login elements:", e)
        driver.quit()
        exit()

    # 6. Wait briefly, then check for successful login or CAPTCHA
    time.sleep(3)

    # 6a. Check if we're at the feed page
    current_url = driver.current_url
    print("Current URL after login:", current_url)

    # 6b. Handle captcha if present (quick check)
    #    If you see a captcha, you'll need to handle it manually or add further logic
    try:
        captcha_div = driver.find_element(By.XPATH, "//div[contains(@class, 'captcha')]")
        if captcha_div.is_displayed():
            print("CAPTCHA detected! Please solve it manually...")
            time.sleep(60)  # wait for manual solve
    except NoSuchElementException:
        pass  # No captcha found

    # 7. If LinkedIn sends us directly to feed, navigate to the invitation manager
    #    Otherwise, we attempt to go directly anyway
    print("Navigating to invitation manager page...")
    driver.get("https://www.linkedin.com/mynetwork/invitation-manager/")
    time.sleep(3)

    # Double-check the current URL
    print("Current URL after navigating to invites:", driver.current_url)

    # 8. Wait up to 10 seconds for Accept buttons to appear
    wait = WebDriverWait(driver, 10)
    try:
        accept_buttons = wait.until(
            EC.presence_of_all_elements_located((By.XPATH, "//button[contains(@aria-label, 'Accept')]"))
        )
    except TimeoutException:
        accept_buttons = []
        print("No Accept buttons found. Possibly zero invitations or a different aria-label.")
    
    # 9. If we have accept buttons, click them
    if accept_buttons:
        print(f"Found {len(accept_buttons)} 'Accept' buttons. Accepting now...")
        for button in accept_buttons:
            try:
                button.click()
                logging.info("Connection request accepted.")
                # Random sleep to mimic human behavior
                time.sleep(random.uniform(1.5, 3.5))
            except Exception as e:
                logging.error(f"Error clicking 'Accept' button: {e}")
    else:
        print("No invitations to accept or aria-label mismatch.")

    # 10. Optionally, scroll to load more if you have many invites
    max_scrolls = 1  # Increase to 2, 3, or more if you want to load more
    for i in range(max_scrolls):
        print(f"Scrolling down... (Attempt {i+1})")
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
        time.sleep(3)

        # Try to find any new accept buttons that might have loaded
        new_buttons = driver.find_elements(By.XPATH, "//button[contains(@aria-label, 'Accept')]")
        print(f"Found {len(new_buttons)} 'Accept' buttons after scrolling.")
        for b in new_buttons:
            try:
                b.click()
                logging.info("Connection request accepted (after scroll).")
                time.sleep(random.uniform(1.5, 3.5))
            except Exception as e:
                logging.error(f"Error clicking 'Accept' button: {e}")

except Exception as e:
    logging.error(f"Unexpected script error: {e}")

finally:
    driver.quit()
    logging.info("Script finished.")