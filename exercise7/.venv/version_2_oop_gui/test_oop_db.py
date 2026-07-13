import unittest
import os
import sqlite3
import math
from db_manager import DatabaseManager
from migrations import create_tables


class TestDatabaseManager(unittest.TestCase):
    def setUp(self):
        """Создает временную базу данных в памяти для каждого теста."""
        self.db_path = ":memory:"
        self.conn = sqlite3.connect(self.db_path)
        create_tables(self.conn)

        # Наполняем тестовыми данными
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO markets (fmid, market_name, city, state, zip, latitude, longitude) VALUES (?,?,?,?,?,?,?)",
            ("TEST01", "Alpha Market", "Boston", "MA", "02101", 42.3601, -71.0589))
        cursor.execute(
            "INSERT INTO markets (fmid, market_name, city, state, zip, latitude, longitude) VALUES (?,?,?,?,?,?,?)",
            ("TEST02", "Beta Market", "Austin", "TX", "73301", 30.2672, -97.7431))
        self.conn.commit()

        # Инициализируем менеджер
        self.db = DatabaseManager(self.db_path)

        # Переопределяем функции в нашей текущей активной conn
        self.conn.create_function("acos", 1, math.acos)
        self.conn.create_function("cos", 1, math.cos)
        self.conn.create_function("sin", 1, math.sin)
        self.conn.create_function("radians", 1, math.radians)
        self.conn.row_factory = sqlite3.Row
        self.db._get_connection = lambda: self.conn

    def tearDown(self):
        self.conn.close()

    def test_pagination_and_filtering(self):
        """Тест фильтрации по штату и пагинации."""
        markets, total = self.db.get_markets_paginated(page=1, per_page=1, state="MA")
        self.assertEqual(total, 1)
        self.assertEqual(len(markets), 1)
        self.assertEqual(markets[0].market_name, "Alpha Market")

    def test_add_and_get_reviews(self):
        """Тест ООП-добавления рецензий с привязкой к пользователю."""
        markets, _ = self.db.get_markets_paginated(page=1, per_page=2)
        market_id = markets[0].db_id

        self.db.add_review(market_id, "Ivan", "Ivanov", 5, "Excellent!")
        reviews = self.db.get_market_reviews(market_id)

        self.assertEqual(len(reviews), 1)
        self.assertEqual(reviews[0].rating, 5)
        self.assertEqual(reviews[0].user.full_name, "Ivan Ivanov")

    def test_cascade_deletion(self):
        """Тест каскадного удаления: удаляя рынок, СУБД должна стереть его отзывы."""
        markets, _ = self.db.get_markets_paginated(page=1, per_page=1)
        m_id = markets[0].db_id

        self.db.add_review(m_id, "Petr", "Petrov", 4, "Good")
        success = self.db.delete_market(m_id)

        self.assertTrue(success)
        # Проверяем, что отзывов в базе больше нет
        cursor = self.conn.execute("SELECT COUNT(*) FROM reviews WHERE market_id = ?", (m_id,))
        self.assertEqual(cursor.fetchone()[0], 0)


if __name__ == '__main__':
    unittest.main()
