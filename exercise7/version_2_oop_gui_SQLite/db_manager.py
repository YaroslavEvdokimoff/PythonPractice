import sqlite3
import math
from typing import List, Optional, Tuple
from models import Market, User, Review


class DatabaseManager:
    """Класс для управления подключением и выполнения запросов к СУБД SQLite (ООП паттерн Repository)."""

    def __init__(self, db_path: str):
        self.db_path = db_path

    def _get_connection(self) -> sqlite3.Connection:
        """Возвращает подключение с зарегистрированными математическими функциями для расчета миль."""
        conn = sqlite3.connect(self.db_path)
        
        # Включаем поддержку внешних ключей (foreign keys) для каскадного удаления
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
                              c_lat: float = None, c_lon: float = None, max_miles: float = None) -> Tuple[List[Market], int]:
        """
        Комплексный метод: Пагинация + Фильтрация + Сортировка + Расчет дистанции.
        Гарантирует точный подсчет страниц и предотвращает сбои тригонометрии SQLite.
        """
        offset = (page - 1) * per_page
        order = "DESC" if reverse else "ASC"

        # Формируем базовые фильтры таблицы рынков
        where_clauses = ["1=1"]
        where_params = []

        if city:
            where_clauses.append("m.city LIKE ?")
            where_params.append(f"%{city}%")
        if state:
            where_clauses.append("m.state LIKE ?")
            where_params.append(f"%{state}%")
        if zip_code:
            where_clauses.append("m.zip LIKE ?")
            where_params.append(f"%{zip_code.strip()}%")

        where_str = " AND ".join(where_clauses)

        # Вычисляем дистанцию (Формула Гаверсинуса)
        if c_lat is not None and c_lon is not None:
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
        else:
            distance_sql = "NULL"

        # Создаем общее логическое выражение (Подзапрос), общее для основного запроса и счетчика страниц
        subquery_filter = ""
        subquery_params = []
        if c_lat is not None and c_lon is not None and max_miles is not None:
            subquery_filter = "WHERE distance IS NOT NULL AND distance <= ?"
            subquery_params.append(max_miles)

        # Подготовка правил сортировки
        sort_map = {
            'rating': f'avg_rating {order}',
            'city_state': f'state {order}, city {order}',
            'distance': f'CASE WHEN distance IS NULL THEN 1 ELSE 0 END, distance {order}',
            'market_name': f'market_name {order}'
        }
        sort_column = sort_map.get(sort_by, f'market_name {order}')

        # Единый каркас выборки данных со всеми агрегациями
        full_wrapper_query = f"""
            SELECT * FROM (
                SELECT m.*, 
                       {distance_sql} AS distance,
                       COALESCE(AVG(r.rating), 0.0) AS avg_rating,
                       COUNT(r.id) AS reviews_count
                FROM markets m
                LEFT JOIN reviews r ON m.id = r.market_id
                WHERE {where_str}
                GROUP BY m.id
            )
            {subquery_filter}
        """

        # Строим итоговые SQL-выражения
        count_query = f"SELECT COUNT(*) AS total FROM ({full_wrapper_query})"
        main_query = f"{full_wrapper_query} ORDER BY {sort_column} LIMIT ? OFFSET ?"

        # Сбор параметров
        base_params = where_params + subquery_params

        with self._get_connection() as conn:
            # 1. Считаем точное количество записей
            res_count = conn.execute(count_query, base_params).fetchone()
            total_records = res_count['total'] if res_count else 0

            # 2. Выгружаем саму страницу данных для Treeview
            final_params = base_params + [per_page, offset]
            cursor = conn.execute(main_query, final_params)
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
        """Добавляет рецензию, автоматически связывая её с пользователем."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM users WHERE first_name = ? AND last_name = ?", (first_name, last_name))
            user_row = cursor.fetchone()

            if user_row:
                user_id = user_row['id']
            else:
                cursor.execute("INSERT INTO users (first_name, last_name) VALUES (?, ?)", (first_name, last_name))
                user_id = cursor.lastrowid

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
