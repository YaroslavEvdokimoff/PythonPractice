import sqlite3
import csv
import os

# Пути относительно файла миграций
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, "data", "Export.csv")
DB_PATH = os.path.join(BASE_DIR, "data", "markets.db")


def create_tables(conn):
    """Создает структуру таблиц в СУБД SQLite."""
    cursor = conn.cursor()

    # Включаем поддержку внешних ключей (foreign keys) для каскадного удаления
    cursor.execute("PRAGMA foreign_keys = ON;")

    # 1. Таблица фермерских рынков
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS markets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fmid TEXT UNIQUE,
        market_name TEXT,
        street TEXT,
        city TEXT,
        state TEXT,
        zip TEXT,
        latitude REAL,
        longitude REAL
    );
    """)

    # 2. Таблица пользователей (ФИО)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT,
        last_name TEXT,
        UNIQUE(first_name, last_name)
    );
    """)

    # 3. Таблица рецензий (связывает рынок и пользователя)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        market_id INTEGER,
        user_id INTEGER,
        rating INTEGER NOT NULL,
        review_text TEXT,
        FOREIGN KEY (market_id) REFERENCES markets(id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)
    conn.commit()


def import_csv_to_db():
    """Читает Export.csv и пачками (bulk) загружает данные в СУБД для скорости."""
    if not os.path.exists(CSV_PATH):
        print(f"[Ошибка]: Исходный файл {CSV_PATH} не найден. Перенесите Export.csv в папку data/.")
        return

    print("Подключение к СУБД SQLite и создание таблиц...")
    conn = sqlite3.connect(DB_PATH)
    create_tables(conn)

    cursor = conn.cursor()

    # Проверяем, не загружены ли данные ранее, чтобы не дублировать
    cursor.execute("SELECT COUNT(*) FROM markets;")
    if cursor.fetchone()[0] > 0:
        print("Данные в СУБД уже были импортированы ранее.")
        conn.close()
        return

    print("Начало импорта данных из CSV в СУБД (это может занять несколько секунд)...")

    with open(CSV_PATH, mode='r', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)

        markets_batch = []
        for row in reader:
            # Мапим колонки из CSV. В Export.csv координаты часто лежат в 'y' (Lat) и 'x' (Lon)
            try:
                lat = float(row.get('y')) if row.get('y') else None
                lon = float(row.get('x')) if row.get('x') else None
            except ValueError:
                lat, lon = None, None

            markets_batch.append((
                row.get('FMID'),
                row.get('MarketName'),
                row.get('street'),
                row.get('City'),
                row.get('State'),
                row.get('zip'),
                lat,
                lon
            ))

            # Сбрасываем в базу пачками по 1000 строк для экономии памяти
            if len(markets_batch) >= 1000:
                cursor.executemany("""
                INSERT OR IGNORE INTO markets (fmid, market_name, street, city, state, zip, latitude, longitude)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                """, markets_batch)
                markets_batch = []

        if markets_batch:
            cursor.executemany("""
            INSERT OR IGNORE INTO markets (fmid, market_name, street, city, state, zip, latitude, longitude)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            """, markets_batch)

    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM markets;")
    total_inserted = cursor.fetchone()[0]
    print(f"Миграция завершена! Успешно импортировано {total_inserted} записей фермерских рынков в СУБД.")
    conn.close()


if __name__ == '__main__':
    import_csv_to_db()
