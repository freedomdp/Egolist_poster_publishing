import os
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.logger import logger
from core.login_handler import login

class SeleniumAutomation:
    def __init__(self):
        self.driver = None

    def start_browser(self):
        try:
            # Попытка запустить Firefox
            firefox_options = FirefoxOptions()
            firefox_options.add_argument('--start-maximized')

            service = FirefoxService(GeckoDriverManager().install())
            self.driver = webdriver.Firefox(service=service, options=firefox_options)
            logger.info("Firefox browser started successfully")
        except Exception as firefox_error:
            logger.warning(f"Failed to start Firefox: {str(firefox_error)}")
            logger.info("Attempting to start Chrome as a fallback...")

            try:
                # Попытка запустить Chrome как резервный вариант
                chrome_options = ChromeOptions()
                chrome_options.add_argument('--start-maximized')
                chrome_options.add_argument('--disable-extensions')
                chrome_options.add_argument('--disable-gpu')
                chrome_options.add_argument('--no-sandbox')
                chrome_options.add_argument('--disable-dev-shm-usage')

                service = ChromeService(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                logger.info("Chrome browser started successfully as a fallback")
            except Exception as chrome_error:
                logger.error(f"Failed to start Chrome: {str(chrome_error)}")
                raise Exception("Failed to start both Firefox and Chrome browsers")

    def perform_login(self, url, username, password):
        if not self.driver:
            self.start_browser()

        logger.info("Attempting to login")
        success = login(self.driver, url, username, password)
        if not success:
            logger.error("Login failed")
            raise Exception("Login failed")
        logger.info("Login process completed")

        # Переход на страницу со списком афиш
        logger.info("Navigating to events list page")
        self.driver.get("https://admin.egolist.ua/events/list")
        try:
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "table.el-table__body"))
            )
            logger.info("Successfully navigated to events list page")
        except Exception as e:
            logger.error(f"Failed to navigate to events list page: {str(e)}")
            raise Exception("Failed to navigate to events list page")

        return True

    def close_browser(self):
        if self.driver:
            self.driver.quit()
            logger.info("Browser closed") 
