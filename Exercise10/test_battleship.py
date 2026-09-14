import os
import unittest
import tkinter as tk
import random
import tkinter.messagebox as msgbox

# Импортируем компоненты игры
import battleship
from battleship import BattleshipGame, load_json, DEFAULT_CONFIG


class TestBattleshipGame(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Инициализируем скрытое окно Tkinter для поддержки UI-элементов в тестах
        cls.root = tk.Tk()
        cls.root.withdraw()

        # Перенаправляем файлы сохранения во временные пути, чтобы не портить статистику игрока
        battleship.CONFIG_FILE = "temp_test_config.json"
        battleship.SCORES_FILE = "temp_test_highscores.json"

    def setUp(self):
        # Отключаем всплывающие окна messagebox и шторку Hotseat, чтобы тесты не зависали
        msgbox.showinfo = lambda title, message: None
        BattleshipGame.show_screen_blanker = lambda self_obj, msg, cb: cb()

        # Заглушка для асинхронных вызовов after (ИИ не ходит сам по таймеру во время тестов)
        self.root.after = lambda delay, callback, *args: None

        # Создаем чистый экземпляр игры для каждого теста
        self.game = BattleshipGame(self.root)

        # Переопределяем метод завершения игры под новую сигнатуру (принимает 2 аргумента)
        self.game.end_game = lambda winner_type, winner_id=1: setattr(self.game, 'game_over', True)

    def tearDown(self):
        pass

    @classmethod
    def tearDownClass(cls):
        # Закрываем Tkinter и удаляем временные файлы строго после завершения всех тестов
        cls.root.destroy()
        for filename in ["temp_test_config.json", "temp_test_highscores.json"]:
            if os.path.exists(filename):
                try:
                    os.remove(filename)
                except:
                    pass

    # --- ГРУППА 1: ИНИЦИАЛИЗАЦИЯ И РАЗМЕРНОСТЬ ПОЛЕЙ ---

    def test_1_board_dimensions(self):
        """Проверка корректности размеров игровых матриц 10х10."""
        self.assertEqual(len(self.game.board1), 10)
        self.assertEqual(len(self.game.board2), 10)
        self.assertEqual(len(self.game.board1[0]), 10)

    def test_2_fleet_deck_count(self):
        """Проверка общего количества палуб сгенерированного флота (должно быть ровно 20 палуб)."""
        decks_player1 = sum(sum(row) for row in self.game.board1)
        decks_player2 = sum(sum(row) for row in self.game.board2)
        self.assertEqual(decks_player1, 20)
        self.assertEqual(decks_player2, 20)

    # --- ГРУППА 2: ВАЛИДАЦИЯ ПРАВИЛ РАССТАНОВКИ КОРАБЛЕЙ ---

    def test_3_can_place_valid_position(self):
        """Проверка возможности легальной установки корабля на пустую доску."""
        empty_board = [[0 for _ in range(10)] for _ in range(10)]
        can_place = self.game.can_place(empty_board, r=2, c=2, length=3, orient="V")
        self.assertTrue(can_place)

    def test_4_can_place_out_of_bounds(self):
        """Проверка блокировки установки корабля, выходящего за границы игрового поля."""
        empty_board = [[0 for _ in range(10)] for _ in range(10)]
        can_place = self.game.can_place(empty_board, r=0, c=8, length=4, orient="H")
        self.assertFalse(can_place)

    def test_5_can_place_overlapping(self):
        """Проверка запрета на пересечение кораблей."""
        test_board = [[0 for _ in range(10)] for _ in range(10)]
        test_board[3][3] = 1  # Существующий корабль
        can_place = self.game.can_place(test_board, r=3, c=1, length=4, orient="H")
        self.assertFalse(can_place)

    def test_6_can_place_touching_border_or_corner(self):
        """Проверка запрета установки корабля вплотную (касание бортом или углом)."""
        test_board = [[0 for _ in range(10)] for _ in range(10)]
        test_board[4][4] = 1
        # Касание по горизонтальной линии справа
        can_touch_side = self.game.can_place(test_board, r=4, c=5, length=1, orient="H")
        # Касание по диагонали (угол)
        can_touch_corner = self.game.can_place(test_board, r=5, c=5, length=1, orient="H")
        self.assertFalse(can_touch_side)
        self.assertFalse(can_touch_corner)

    # --- ГРУППА 3: МЕХАНИКА ВЫСТРЕЛОВ И ПОДТВЕРЖДЕНИЕ ПОПАДАНИЙ ---

    def test_7_player_shoot_hit(self):
        """Проверка логики успешного попадания игрока по палубе ИИ."""
        self.game.config["game_mode"] = "vs Computer"
        self.game.board2 = [[0 for _ in range(10)] for _ in range(10)]
        self.game.shots1 = [[0 for _ in range(10)] for _ in range(10)]
        self.game.board2[1][1] = 1  # Размещаем тестовую мишень

        self.game.player_shoot(1, 1)
        self.assertEqual(self.game.shots1[1][1], 2)  # Статус 2 означает попадание (Крестик)

    def test_8_player_shoot_miss(self):
        """Проверка логики промаха по пустой клетке."""
        self.game.config["game_mode"] = "vs Computer"
        self.game.board2 = [[0 for _ in range(10)] for _ in range(10)]
        self.game.shots1 = [[0 for _ in range(10)] for _ in range(10)]

        self.game.player_shoot(2, 2)
        self.assertEqual(self.game.shots1[2][2], 1)  # Статус 1 означает промах (Точка)

    def test_9_player_shoot_already_shot_cell(self):
        """Проверка игнорирования повторного выстрела в одну и ту же координату."""
        self.game.shots1 = [[0 for _ in range(10)] for _ in range(10)]
        self.game.shots1[5][5] = 1  # Туда уже стреляли ранее
        res = self.game.player_shoot(5, 5)
        self.assertIsNone(res)  # Метод должен мгновенно прерваться и вернуть None

    # --- ГРУППА 4: АЛГОРИТМЫ ПОИСКА И УНИЧТОЖЕНИЯ СУДОВ (BFS) ---

    def test_10_find_entire_ship_multi_deck(self):
        """Проверка волнового обхода BFS для поиска всех палуб многопалубного корабля."""
        test_board = [[0 for _ in range(10)] for _ in range(10)]
        test_board[2][2] = 1
        test_board[2][3] = 1
        test_board[2][4] = 1

        ship_cells = self.game.find_entire_ship(test_board, r=2, c=3)
        self.assertEqual(len(ship_cells), 3)
        self.assertIn((2, 2), ship_cells)
        self.assertIn((2, 4), ship_cells)

    def test_11_check_and_mark_sunk_surroundings(self):
        """Проверка автоматической отметки промахов вокруг полностью уничтоженного судна."""
        test_board = [[0 for _ in range(10)] for _ in range(10)]
        test_shots = [[0 for _ in range(10)] for _ in range(10)]
        test_board[0][0] = 1
        test_shots[0][0] = 2  # Корабль подбит

        is_sunk = self.game.check_and_mark_sunk(test_board, test_shots, r=0, c=0)
        self.assertTrue(is_sunk)
        # Соседние клетки должны автоматически заполниться точками (статус 1)
        self.assertEqual(test_shots[0][1], 1)
        self.assertEqual(test_shots[1][0], 1)
        self.assertEqual(test_shots[1][1], 1)

    # --- ГРУППА 5: СОСТОЯНИЯ ИГРЫ И ИСКУССТВЕННЫЙ ИНТЕЛЛЕКТ ---

    def test_12_game_over_interaction_blocker(self):
        """Проверка заморозки поля: выстрелы после завершения игры не регистрируются."""
        self.game.game_over = True
        self.game.shots1 = [[0 for _ in range(10)] for _ in range(10)]
        self.game.player_shoot(0, 0)
        self.assertEqual(self.game.shots1[0][0], 0)

    def test_13_ai_memory_cleanup_on_sink(self):
        """Проверка очистки стека целей ИИ после полного уничтожения корабля."""
        self.game.config["difficulty"] = "Normal"
        self.game.board1 = [[0 for _ in range(10)] for _ in range(10)]
        self.game.shots2 = [[0 for _ in range(10)] for _ in range(10)]

        self.game.board1[0][0] = 1
        self.game.ai_targets = [(0, 0)]

        # Подменяем генератор случайного выбора, имитируя точный выстрел компьютера
        old_choice = random.choice
        random.choice = lambda cells: (0, 0)

        self.game.comp_shoot()

        random.choice = old_choice
        # Стек целей должен очиститься, так как однопалубный корабль на (0,0) потоплен
        self.assertNotIn((0, 0), self.game.ai_targets)

    def test_14_check_win_condition(self):
        """Проверка детектора условий победы матча."""
        test_board = [[0 for _ in range(10)] for _ in range(10)]
        test_shots = [[0 for _ in range(10)] for _ in range(10)]
        test_board[5][5] = 1

        # Пока палуба не повреждена, победа не засчитывается
        self.assertFalse(self.game.check_win(test_board, test_shots))
        # Палуба уничтожена
        test_shots[5][5] = 2
        self.assertTrue(self.game.check_win(test_board, test_shots))

    def test_15_config_json_loader(self):
        """Тестирование стабильности JSON-модуля при загрузке базовых параметров конфигурации."""
        config = load_json("temp_test_config.json", DEFAULT_CONFIG)
        self.assertIn("difficulty", config)
        self.assertEqual(config["difficulty"], "Normal")


if __name__ == "__main__":
    unittest.main()
