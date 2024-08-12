from datetime import datetime, date
from typing import List
from models.event import Event
from models.sheet_event import SheetEvent
from utils.logger import logger

def find_duplicates(site_events: List[Event], sheet_events: List[SheetEvent]) -> List[tuple]:
    duplicates = []
    for site_event in site_events:
        for sheet_event in sheet_events:
            if is_duplicate(site_event, sheet_event):
                duplicates.append((site_event, sheet_event))
                logger.info(f"Найден дубликат: {site_event.name} ({site_event.date})")
    return duplicates

def is_duplicate(event1: Event, event2: SheetEvent) -> bool:
    return (
        event1.name.lower() == event2.name.lower() and
        event1.date == event2.date and
        event1.venue.lower() == event2.venue.lower()
    )

def find_old_events(events: List[Event], cutoff_date: date = None) -> List[Event]:
    if cutoff_date is None:
        cutoff_date = date.today()

    old_events = [event for event in events if event.date < cutoff_date]
    for event in old_events:
        logger.info(f"Найдено устаревшее событие: {event.name} ({event.date})")
    return old_events

def process_events(site_events: List[Event], sheet_events: List[SheetEvent]) -> dict:
    result = {
        "duplicates": find_duplicates(site_events, sheet_events),
        "old_events": find_old_events(site_events),
        "new_events": []
    }

    # Находим новые события (те, которых нет на сайте, но есть в таблице)
    site_event_names = set(event.name.lower() for event in site_events)
    result["new_events"] = [
        event for event in sheet_events
        if event.name.lower() not in site_event_names and event.date >= date.today()
    ]

    logger.info(f"Найдено дубликатов: {len(result['duplicates'])}")
    logger.info(f"Найдено устаревших событий: {len(result['old_events'])}")
    logger.info(f"Найдено новых событий для публикации: {len(result['new_events'])}")

    return result
