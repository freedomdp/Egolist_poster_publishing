import gspread
from google.oauth2.service_account import Credentials
from models.sheet_event import SheetEvent
from datetime import datetime
from typing import List
import os

def get_events_from_sheet() -> List[SheetEvent]:
    # Путь к файлу с учетными данными сервисного аккаунта
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    creds_file = os.path.join(project_root, 'credentials', 'credentials.json')

    # Проверка существования файла
    if not os.path.exists(creds_file):
        raise FileNotFoundError(f"Файл с учетными данными не найден: {creds_file}")

    # Настройка учетных данных
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = Credentials.from_service_account_file(creds_file, scopes=scope)
    client = gspread.authorize(creds)

    # Открытие таблицы по URL
    sheet_url = 'https://docs.google.com/spreadsheets/d/1L-HKqOh58Z3PR89JQRJkqEN7XJ3f3nWW4TLTHHUpFCU/edit?gid=0#gid=0'
    sheet = client.open_by_url(sheet_url).worksheet('Data')

    # Получение всех значений
    values = sheet.get_all_values()

    events = []
    for row in values[1:]:  # Пропускаем заголовок
        if row[0] == '0':  # Проверяем отметку о публикации
            try:
                event = SheetEvent(
                    publication_mark=row[0],
                    name=row[1],
                    description=row[2],
                    event_type=row[3],
                    price=row[4],
                    date=datetime.strptime(row[5], "%d.%m.%Y").date(),
                    time=datetime.strptime(row[6], "%H:%M").time() if row[6] else None,
                    city=row[7],
                    venue=row[8],
                    address=row[9],
                    source=row[10],
                    contacts=row[11],
                    photo_url=row[12],
                    video_url=row[13]
                )
                events.append(event)
            except Exception as e:
                print(f"Ошибка при обработке строки: {row}. Ошибка: {str(e)}")

    return events
