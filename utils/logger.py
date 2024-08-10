import logging

def setup_logger():
    logger = logging.getLogger('egolist_poster')
    logger.setLevel(logging.INFO)

    # Создаем обработчик для вывода в консоль
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Создаем форматтер
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)

    # Добавляем обработчик к логгеру
    logger.addHandler(console_handler)

    return logger

# Создаем и настраиваем логгер
logger = setup_logger()
