import traceback
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QTextEdit, QLabel
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont
from core.selenium_automation import SeleniumAutomation
from core.parsing import parse_events
from utils.config_handler import load_config
from utils.logger import logger

class WorkerThread(QThread):
    update_log = pyqtSignal(str)
    update_counters = pyqtSignal(int, int, int)
    update_table = pyqtSignal(int, list)

    def run(self):
        automation = None
        try:
            self.update_log.emit("Начало процесса входа...")
            logger.info("Начало процесса входа")

            config = load_config()
            automation = SeleniumAutomation()
            automation.perform_login(config['LOGIN_URL'], config['LOGIN_EMAIL'], config['LOGIN_PASSWORD'])

            self.update_log.emit("Вход выполнен успешно, начинаем парсинг...")
            logger.info("Вход выполнен успешно, начинаем парсинг")

            events = parse_events(automation.driver,
                                  lambda count: self.update_counters.emit(0, 0, count),
                                  lambda page, page_events: self.update_table.emit(page, page_events))

            self.update_log.emit(f"Парсинг завершен. Всего найдено событий: {len(events)}")
            logger.info(f"Парсинг завершен. Всего найдено событий: {len(events)}")

        except Exception as e:
            error_msg = f"Произошла ошибка: {str(e)}\n{traceback.format_exc()}"
            self.update_log.emit(error_msg)
            logger.error(error_msg)
        finally:
            if automation:
                automation.close_browser()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Публикация афиш")
        self.resize(1000, 800)
        self.total_events = 0

        self.start_button = QPushButton("Запустить")
        self.start_button.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px;")
        self.start_button.clicked.connect(self.start_process)

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        font = QFont()
        font.setPointSize(8)
        self.log_output.setFont(font)

        self.sheets_counter = QLabel("Афиши из таблицы: 0 | Опубликовано: 0")
        self.parser_counter = QLabel("Афиши на сайте: 0")

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
        self.worker_thread.update_table.connect(self.update_table)

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

    def update_table(self, page, events):
        self.log_output.append(f"\nСтраница {page}")
        self.log_output.append(
            f"| {'№':3} | {'Название                 ':25} | {'Место          ':15} | {'Дата      ':10} | {'Время':5} | {'Тип            ':15} |"
        )
        self.log_output.append(
            "--------------------------------------------------------------------------------------"
        )
        for event in events:
            self.total_events += 1
            time_display = event.time.strftime("%H:%M") if event.time else "     "
            self.log_output.append(
                f"| {self.total_events:3d} | "
                f"{event.name[:25].ljust(25)} | "
                f"{event.venue[:15].ljust(15)} | "
                f"{str(event.date):<10} | "
                f"{time_display:<5} | "
                f"{event.event_type[:15].ljust(15)} |"
            )
