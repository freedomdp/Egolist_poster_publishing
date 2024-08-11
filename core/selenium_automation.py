from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from utils.logger import logger
from core.login_handler import login

class SeleniumAutomation:
    def __init__(self):
        self.driver = None

    def start_browser(self):
        chrome_options = ChromeOptions()
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')

        service = ChromeService(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        logger.info("Chrome browser started successfully")

    def perform_login(self, url, username, password):
        if not self.driver:
            self.start_browser()

        logger.info("Attempting to login")
        success = login(self.driver, url, username, password)
        if not success:
            logger.error("Login failed")
            raise Exception("Login failed")
        logger.info("Login process completed")

        # Явно переходим на страницу со списком афиш
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
