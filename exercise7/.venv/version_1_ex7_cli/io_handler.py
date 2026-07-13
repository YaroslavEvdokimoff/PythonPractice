import csv
import os

def load_csv_data(file_path: str) -> list[dict]:
    """Чистая функция для чтения CSV. Возвращает список словарей."""
    if not os.path.exists(file_path):
        return []
    with open(file_path, mode='r', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        return list(reader)
