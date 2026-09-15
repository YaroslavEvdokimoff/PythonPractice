import csv
import os

def load_csv_data(file_path: str) -> list[dict]:
    """
    Безопасно считывает данные из CSV-файла.
    Возвращает список словарей. При любых системных ошибках или сбое кодировки
    возвращает пустой список, предотвращая аварийное падение программы.
    """
    if not os.path.exists(file_path):
        return []
    try:
        with open(file_path, mode='r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            return list(reader)
    except (UnicodeDecodeError, IOError, csv.Error):
        return []
