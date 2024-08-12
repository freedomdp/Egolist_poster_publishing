import traceback
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QTextEdit, QLabel
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont
from core.selenium_automation import SeleniumAutomation
from core.parsing import parse_events
from core.google_sheets_handler import get_events_from_sheet
from utils.config_handler import load_config
from utils.logger import logger
from models.sheet_event import SheetEvent

class WorkerThread(QThread):
    update_log = pyqtSignal(str)
    update_counters = pyqtSignal(int, int, int)
    update_table = pyqtSignal(int, list)

    def run(self):
        automation = None
        try:
            self.update_log.emit("Начало процесса авторизации на сайте...")
            logger.info("Начало процесса авторизации на сайте")

            config = load_config()
            automation = SeleniumAutomation()

            try:
                automation.perform_login(config['LOGIN_URL'], config['LOGIN_EMAIL'], config['LOGIN_PASSWORD'])
            except Exception as e:
                self.update_log.emit(f"Ошибка при запуске браузера или входе в систему: {str(e)}")
                logger.error(f"Ошибка при запуске браузера или входе в систему: {str(e)}")
                return

            self.update_log.emit("Авторизация выполнена успешно")
            logger.info("Авторизация выполнена успешно")

            # 2. Парсинг афиш с сайта admin.egolist.ua
            self.update_log.emit("Начало парсинга афиш с сайта...")
            logger.info("Начало парсинга афиш с сайта")

            site_events = parse_events(automation.driver,
                                       lambda count: self.update_counters.emit(0, 0, count),
                                       lambda page, page_events: self.update_table.emit(page, page_events))

            self.update_log.emit(f"Парсинг завершен. Всего найдено событий на сайте: {len(site_events)}")
            logger.info(f"Парсинг завершен. Всего найдено событий на сайте: {len(site_events)}")

            # 3. Получение данных из гугл таблицы
            self.update_log.emit("Начало получения данных из Google таблицы...")
            logger.info("Начало получения данных из Google таблицы")

            sheet_events = get_events_from_sheet()
            self.update_log.emit(f"Получено {len(sheet_events)} событий из Google таблицы")
            logger.info(f"Получено {len(sheet_events)} событий из Google таблицы")

            self.update_counters.emit(len(sheet_events), 0, len(site_events))
            self.update_table.emit(0, sheet_events)

            # Здесь можно добавить дополнительную логику для сравнения или обработки данных

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
        self.update_counters(0, 0, 0)  # Очищаем счетчики
        self.worker_thread.start()

    def update_log(self, message):
        self.log_output.append(message)

    def update_counters(self, total, published, on_site):
        self.sheets_counter.setText(f"Афиши из таблицы: {total} | Опубликовано: {published}")
        self.parser_counter.setText(f"Афиши на сайте: {on_site}")

    def update_table(self, page, events):
        if isinstance(events[0], SheetEvent):
            self.log_output.append("\nСобытия из Google таблицы:")
            self.total_events = 0  # Сбрасываем счетчик для событий из таблицы
        else:
            self.log_output.append(f"\nСтраница {page} событий с сайта:")

        self.log_output.append(
            f"| {'№':3} | {'Название':25} | {'Место':15} | {'Дата':10} | {'Время':5} | {'Тип':15} |"
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
