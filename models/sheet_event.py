from dataclasses import dataclass
from datetime import date, time
from typing import Optional

@dataclass
class SheetEvent:
    publication_mark: str
    name: str
    description: str
    event_type: str
    price: str
    date: date
    time: Optional[time]
    city: str
    venue: str
    address: str
    source: str
    contacts: str
    photo_url: str
    video_url: str

    def __post_init__(self):
        if self.time is not None and self.time == time(0, 0):
            self.time = None

    def __hash__(self):
        return hash((self.name, self.venue, self.date, self.time, self.event_type))

    def __str__(self):
        time_str = self.time.strftime("%H:%M") if self.time else ""
        return f"Название: {self.name}, Место: {self.venue}, Дата: {self.date}, Время: {time_str}, Тип: {self.event_type}"
