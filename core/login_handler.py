from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.logger import logger
import time

def login(driver: webdriver.Chrome, url: str, username: str, password: str) -> bool:
    logger.info(f"Navigating to: {url}")
    driver.get(url)

    try:
        logger.info("Waiting for login input field")
        login_input = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[autocomplete='name']"))
        )
        login_input.clear()
        login_input.send_keys(username)
        logger.info(f"Entered username: {username}")

        logger.info("Entering password")
        password_input = driver.find_element(By.CSS_SELECTOR, "input[autocomplete='password']")
        password_input.clear()
        password_input.send_keys(password)
        logger.info("Password entered")

        logger.info("Clicking login button")
        login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        login_button.click()

        logger.info("Waiting for 3 seconds after login")
        time.sleep(3)

        logger.info(f"Current URL after login: {driver.current_url}")
        return True
    except Exception as e:
        logger.error(f"Failed during login process: {str(e)}")
        return False
