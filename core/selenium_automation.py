from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from utils.logger import logger
import time

class SeleniumAutomation:
    def __init__(self):
        self.driver = None

    def start_browser(self):
        try:
            chrome_options = ChromeOptions()
            chrome_options.add_argument('--ignore-certificate-errors')
            chrome_options.add_argument('--ignore-ssl-errors')
            chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

            service = ChromeService(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            logger.info("Chrome browser started successfully")
        except Exception as e:
            logger.error(f"Failed to start Chrome: {e}")
            try:
                service = FirefoxService(GeckoDriverManager().install())
                self.driver = webdriver.Firefox(service=service)
                logger.info("Firefox browser started successfully")
            except Exception as e:
                logger.error(f"Failed to start Firefox: {e}")
                raise Exception("Failed to start both Chrome and Firefox")

    def login(self, url, username, password):
        if not self.driver:
            self.start_browser()

        logger.info(f"Navigating to: {url}")
        self.driver.get(url)

        logger.info("Waiting for login input field")
        login_input = WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[autocomplete='name']"))
        )
        time.sleep(2)
        login_input.send_keys(username)

        logger.info("Entering password")
        password_input = self.driver.find_element(By.CSS_SELECTOR, "input[autocomplete='password']")
        time.sleep(2)
        password_input.send_keys(password)

        logger.info("Clicking login button")
        login_button = self.driver.find_element(By.XPATH, "//span[text()=' Войти ']")
        time.sleep(2)
        login_button.click()

        logger.info("Waiting for navigation after login")
        try:
            WebDriverWait(self.driver, 30).until(
                EC.url_contains("admin.egolist.ua")
            )
            logger.info(f"Current URL after login: {self.driver.current_url}")
        except Exception as e:
            logger.error(f"Failed to navigate after login: {str(e)}")
            logger.info(f"Current URL: {self.driver.current_url}")
            logger.info(f"Page source: {self.driver.page_source[:500]}...")
            raise

        logger.info("Login successful")

    def navigate_to_events_list(self):
        logger.info("Navigating to events list page")
        self.driver.get("https://admin.egolist.ua/events/list")

        try:
            WebDriverWait(self.driver, 30).until(
                EC.url_contains("admin.egolist.ua/events/list")
            )
            logger.info(f"Current URL after navigation: {self.driver.current_url}")
        except Exception as e:
            logger.error(f"Failed to navigate to events list page: {str(e)}")
            logger.info(f"Current URL: {self.driver.current_url}")
            logger.info(f"Page source: {self.driver.page_source[:500]}...")
            raise

        logger.info("Successfully navigated to events list page")

    def close_browser(self):
        if self.driver:
            self.driver.quit()
            logger.info("Browser closed")
