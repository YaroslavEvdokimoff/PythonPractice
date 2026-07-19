import sqlite3
import math
from typing import List, Optional
from models import Market, User, Review


class DatabaseManager:
    """Класс для управления подключением и выполнения запросов к СУБД SQLite (ООП паттерн Repository)."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db_features()

    def _init_db_features(self):
        """Включает поддержку внешних ключей при каждом подключении."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA foreign_keys = ON;")

    def _get_connection(self) -> sqlite3.Connection:
        """Возвращает подключение с зарегистрированными математическими функциями для расчета миль."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON;")

        # Регистрируем функции для формулы гаверсинусов в SQL
        conn.create_function("acos", 1, math.acos)
        conn.create_function("cos", 1, math.cos)
        conn.create_function("sin", 1, math.sin)
        conn.create_function("radians", 1, math.radians)

        conn.row_factory = sqlite3.Row  # Доступ к колонкам по именам
        return conn

    def get_markets_paginated(self, page: int, per_page: int,
                              sort_by: str = 'market_name', reverse: bool = False,
                              city: str = "", state: str = "", zip_code: str = "",
                              c_lat: float = None, c_lon: float = None, max_miles: float = None) -> Tuple[
        List[Market], int]:
        """
        Комплексный метод: Пагинация + Фильтрация + Сортировка + Расчет дистанции.
        Возвращает кортеж: (список объектов Market, общее количество найденных записей).
        """
        offset = (page - 1) * per_page
        order = "DESC" if reverse else "ASC"

        where_clauses = ["1=1"]
        params = []

        if city:
            where_clauses.append("m.city LIKE ?")
            params.append(f"%{city}%")
        if state:
            where_clauses.append("m.state LIKE ?")
            params.append(f"%{state}%")
        if zip_code:
            where_clauses.append("m.zip LIKE ?")
            params.append(f"%{zip_code.strip()}%")

        # Формула гаверсинусов на чистом SQL с защитой от пустых (NULL/0) координат
        distance_sql = "NULL"
        if c_lat is not None and c_lon is not None:
            # Считаем только там, где координаты заполнены корректно
            distance_sql = f"""
            CASE 
                WHEN m.latitude IS NOT NULL AND m.longitude IS NOT NULL AND m.latitude != 0 AND m.longitude != 0
                THEN (3959.0 * acos(
                    cos(radians({c_lat})) * cos(radians(m.latitude)) * 
                    cos(radians(m.longitude) - radians({c_lon})) + 
                    sin(radians({c_lat})) * sin(radians(m.latitude))
                ))
                ELSE NULL
            END
            """
            if max_miles is not None:
                # В блоке фильтрации WHERE отсекаем пустые координаты и проверяем радиус
                where_clauses.append(
                    f"m.latitude IS NOT NULL AND m.longitude IS NOT NULL AND m.latitude != 0 AND {distance_sql} <= ?")
                params.append(max_miles)

        where_str = " AND ".join(where_clauses)

        sort_map = {
            'rating': f'avg_rating {order}',
            'city_state': f'm.state {order}, m.city {order}',
            'distance': f'CASE WHEN distance IS NULL THEN 1 ELSE 0 END, distance {order}',
            'market_name': f'm.market_name {order}'
        }
        sort_column = sort_map.get(sort_by, f'm.market_name {order}')

        query = f"""
            SELECT m.*, 
                   {distance_sql} AS distance,
                   COALESCE(AVG(r.rating), 0.0) AS avg_rating,
                   COUNT(r.id) AS reviews_count
            FROM markets m
            LEFT JOIN reviews r ON m.id = r.market_id
            WHERE {where_str}
            GROUP BY m.id
            ORDER BY {sort_column}
            LIMIT ? OFFSET ?
        """

        count_query = f"""
            SELECT COUNT(DISTINCT m.id) AS total FROM markets m
            WHERE {where_str}
        """

        with self._get_connection() as conn:
            # 1. Безопасно получаем общее количество как целое число
            res_count = conn.execute(count_query, params).fetchone()
            total_records = res_count['total'] if res_count else 0

            # 2. Получаем страницу данных
            final_params = params + [per_page, offset]
            cursor = conn.execute(query, final_params)
            rows = cursor.fetchall()

        markets = []
        for row in rows:
            market = Market(
                db_id=row['id'], fmid=row['fmid'], market_name=row['market_name'],
                street=row['street'], city=row['city'], state=row['state'], zip_code=row['zip'],
                latitude=row['latitude'], longitude=row['longitude']
            )
            market.distance = round(row['distance'], 2) if row['distance'] is not None else None
            market.avg_rating = round(row['avg_rating'], 1)
            market.reviews_count = row['reviews_count']
            markets.append(market)

        return markets, total_records

    def get_market_reviews(self, market_id: int) -> List[Review]:
        """Возвращает список всех объектов Review для конкретного рынка."""
        query = """
            SELECT r.id as r_id, r.rating, r.review_text, u.id as u_id, u.first_name, u.last_name
            FROM reviews r
            JOIN users u ON r.user_id = u.id
            WHERE r.market_id = ?
            ORDER BY r.id DESC
        """
        with self._get_connection() as conn:
            rows = conn.execute(query, (market_id,)).fetchall()

        reviews = []
        for row in rows:
            user = User(db_id=row['u_id'], first_name=row['first_name'], last_name=row['last_name'])
            review = Review(
                db_id=row['r_id'], market_id=market_id, user=user,
                rating=row['rating'], review_text=row['review_text']
            )
            reviews.append(review)
        return reviews

    def add_review(self, market_id: int, first_name: str, last_name: str, rating: int, text: str):
        """Добавляет рецензию, автоматически связывая её с пользователем (создает его при необходимости)."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Находим или создаем пользователя (ФИО)
            cursor.execute("SELECT id FROM users WHERE first_name = ? AND last_name = ?", (first_name, last_name))
            user_row = cursor.fetchone()

            if user_row:
                user_id = user_row['id']
            else:
                cursor.execute("INSERT INTO users (first_name, last_name) VALUES (?, ?)", (first_name, last_name))
                user_id = cursor.lastrowid

            # Записываем рецензию
            cursor.execute(
                "INSERT INTO reviews (market_id, user_id, rating, review_text) VALUES (?, ?, ?, ?)",
                (market_id, user_id, rating, text)
            )
            conn.commit()

    def delete_market(self, market_id: int) -> bool:
        """Каскадно удаляет рынок и все его отзывы из СУБД."""
        with self._get_connection() as conn:
            cursor = conn.execute("DELETE FROM markets WHERE id = ?", (market_id,))
            conn.commit()
            return cursor.rowcount > 0
