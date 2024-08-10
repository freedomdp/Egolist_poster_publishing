import traceback
import time
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QTextEdit, QLabel
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont
from core.selenium_automation import SeleniumAutomation
from utils.config_handler import load_config
from utils.logger import logger

class WorkerThread(QThread):
    update_log = pyqtSignal(str)
    update_counters = pyqtSignal(int, int, int)

    def run(self):
        automation = None
        try:
            self.update_log.emit("Starting login process...")
            logger.info("Starting login process")

            config = load_config()
            automation = SeleniumAutomation()
            automation.login(config['LOGIN_URL'], config['LOGIN_EMAIL'], config['LOGIN_PASSWORD'])

            self.update_log.emit("Login successful")
            logger.info("Login successful")

            self.update_log.emit("Navigating to events list page...")
            logger.info("Navigating to events list page")
            automation.navigate_to_events_list()

            self.update_log.emit("Successfully navigated to events list page")
            logger.info("Successfully navigated to events list page")

            # Добавляем явную задержку перед закрытием браузера
            time.sleep(10)

        except Exception as e:
            error_msg = f"An error occurred: {str(e)}\n{traceback.format_exc()}"
            self.update_log.emit(error_msg)
            logger.error(error_msg)
        finally:
            if automation:
                automation.close_browser()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Публикация афиш")
        self.resize(800, 600)

        font = QFont()
        font.setPointSize(12)

        self.start_button = QPushButton("Запустить")
        self.start_button.setFont(font)
        self.start_button.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px;")
        self.start_button.clicked.connect(self.start_process)

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setFont(font)

        self.sheets_counter = QLabel("Афиши из таблицы: 0 | Опубликовано: 0")
        self.sheets_counter.setFont(font)
        self.parser_counter = QLabel("Афиши на сайте: 0")
        self.parser_counter.setFont(font)

        main_layout = QVBoxLayout()
        counter_layout = QHBoxLayout()

        counter_layout.addWidget(self.sheets_counter)
        counter_layout.addWidget(self.parser_counter)

        main_layout.addWidget(self.start_button)
        main_layout.addLayout(counter_layout)
        main_layout.addWidget(self.log_output)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.worker_thread = WorkerThread()
        self.worker_thread.update_log.connect(self.update_log)
        self.worker_thread.update_counters.connect(self.update_counters)

        self.setStyleSheet("""
            QMainWindow {
                background-color: #2C3E50;
            }
            QLabel {
                color: white;
            }
            QTextEdit {
                background-color: #34495E;
                color: white;
                border: none;
            }
        """)

    def start_process(self):
        self.start_button.setEnabled(False)
        self.log_output.clear()
        self.update_log("Запуск процесса...")
        self.worker_thread.start()

    def update_log(self, message):
        self.log_output.append(message)

    def update_counters(self, total, published, on_site):
        self.sheets_counter.setText(f"Афиши из таблицы: {total} | Опубликовано: {published}")
        self.parser_counter.setText(f"Афиши на сайте: {on_site}")
