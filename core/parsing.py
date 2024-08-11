from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from models.event import Event
from datetime import datetime, time
from typing import Set, Callable, List
from utils.logger import logger
import time as time_module

def parse_events(driver: webdriver.Chrome,
                 update_counter: Callable[[int], None],
                 update_table: Callable[[int, List[Event]], None]) -> List[Event]:
    all_events = []
    page = 1
    total_pages = None

    while True:
        logger.info(f"Парсинг страницы {page}")
        page_events = []

        try:
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "table.el-table__body"))
            )
        except Exception as e:
            logger.error(f"Ошибка загрузки страницы {page}: {str(e)}")
            break

        if total_pages is None:
            try:
                pagination = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".el-pagination"))
                )
                page_numbers = pagination.find_elements(By.CSS_SELECTOR, ".el-pager .number")
                total_pages = int(page_numbers[-1].text)
                logger.info(f"Всего страниц: {total_pages}")
            except Exception as e:
                logger.error(f"Ошибка определения общего количества страниц: {str(e)}")
                total_pages = 1

        rows = driver.find_elements(By.CSS_SELECTOR, "table.el-table__body tr")

        for row in rows:
            try:
                columns = row.find_elements(By.TAG_NAME, "td")
                if len(columns) >= 6:
                    name = columns[1].text.strip()
                    venue = columns[2].text.strip()
                    event_date = columns[3].text.strip()
                    event_time = columns[4].text.strip()
                    event_type = columns[5].text.strip()

                    try:
                        event_date = datetime.strptime(event_date, "%Y-%m-%d").date()
                    except ValueError:
                        logger.warning(f"Некорректная дата: {event_date} для события: {name}")
                        continue

                    if event_time:
                        try:
                            event_time = datetime.strptime(event_time, "%H:%M").time()
                        except ValueError:
                            logger.warning(f"Некорректное время: {event_time} для события: {name}")
                            event_time = None
                    else:
                        event_time = None

                    event = Event(name, venue, event_date, event_time, event_type)
                    all_events.append(event)
                    page_events.append(event)
            except Exception as e:
                logger.error(f"Ошибка парсинга строки: {str(e)}")

        logger.info(f"Обработано событий на странице {page}: {len(page_events)}")
        update_counter(len(all_events))
        update_table(page, page_events)

        if page == total_pages:
            break

        try:
            next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn-next"))
            )
            next_button.click()
            logger.info(f"Переход на страницу {page + 1}")
            time_module.sleep(3)
        except Exception as e:
            logger.error(f"Ошибка при переходе на следующую страницу: {str(e)}")
            break

        page += 1

    logger.info(f"Парсинг завершен. Всего найдено событий: {len(all_events)}")
    return all_events
