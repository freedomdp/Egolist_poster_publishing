import sys
import os

# Получаем абсолютный путь к директории, содержащей main.py
current_dir = os.path.dirname(os.path.abspath(__file__))
# Добавляем родительскую директорию текущей директории в sys.path
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from PyQt6.QtWidgets import QApplication
from Egolist_poster_publishing.gui.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
