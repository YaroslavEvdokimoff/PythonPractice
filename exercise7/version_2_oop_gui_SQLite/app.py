import sys
import os
import tkinter as tk
from db_manager import DatabaseManager
from gui_views import MarketAppGUI

# Автоматически определяем абсолютный путь к файлу СУБД в папке data/
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "markets.db")


def main():
    """Главная точка входа для запуска графической версии приложения (ООП + СУБД)."""

    # Проверяем, выполнил ли администратор скрипт миграции данных
    if not os.path.exists(DB_PATH):
        print("=" * 70)
        print(f"[Критическая ошибка]: Файл СУБД по адресу {DB_PATH} не найден.")
        print("Перед первым запуском графического интерфейса необходимо импортировать данные!")
        print("Пожалуйста, выполните команду: python migrations.py")
        print("=" * 70)
        input("Нажмите Enter для выхода...")
        sys.exit(1)

    # Инициализируем корневой объект оконной системы Tkinter
    root = tk.Tk()

    # Создаем экземпляр менеджера СУБД (Слой данных / Паттерн Репозиторий)
    db_manager = DatabaseManager(DB_PATH)

    # Инициализируем графическую оболочку и передаем ей управление базой данных
    app = MarketAppGUI(root, db_manager)

    # Запускаем бесконечный цикл обработки системных событий окна (клики, ввод, отрисовка)
    root.mainloop()


if __name__ == '__main__':
    main()
