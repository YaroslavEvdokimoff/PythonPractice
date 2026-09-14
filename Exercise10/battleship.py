import os
import json
import random
import tkinter as tk
from tkinter import messagebox, ttk

CONFIG_FILE = "config.json"
SCORES_FILE = "highscores.json"

DEFAULT_CONFIG = {
    "window_size": "900x650",
    "bg_color": "#2c3e50",
    "grid_color": "#34495e",
    "font_family": "Arial",
    "font_size": 12,
    "game_mode": "vs Computer",
    "difficulty": "Normal"
}

DEFAULT_SCORES = [
    {"name": "Игрок 1", "wins": 0},
    {"name": "Игрок 2", "wins": 0},
    {"name": "Computer", "wins": 0}
]

def load_json(filename, default_data):
    if not os.path.exists(filename):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(default_data, f, ensure_ascii=False, indent=4)
        return default_data
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(default_data, f, ensure_ascii=False, indent=4)
        return default_data

def save_json(filename, data):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

class BattleshipGame:
    def __init__(self, root):
        self.root = root
        self.config = load_json(CONFIG_FILE, DEFAULT_CONFIG)
        self.scores = load_json(SCORES_FILE, DEFAULT_SCORES)
        
        self.root.title("Морской Бой")
        self.root.geometry(self.config.get("window_size", "900x650"))
        self.root.configure(bg=self.config.get("bg_color", "#2c3e50"))
        
        self.board1 = [[0 for _ in range(10)] for _ in range(10)]
        self.board2 = [[0 for _ in range(10)] for _ in range(10)]
        self.shots1 = [[0 for _ in range(10)] for _ in range(10)]
        self.shots2 = [[0 for _ in range(10)] for _ in range(10)]
        
        self.ai_targets = []
        self.active_timers = []  
        
        self.left_buttons = {}
        self.right_buttons = {}
        self.game_over = False
        self.actions_blocked = False  
        self.current_turn = 1  
        
        self.create_menu()
        
        self.main_frame = tk.Frame(self.root, bg=self.config["bg_color"])
        self.main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        self.info_label = tk.Label(self.main_frame, text="", fg="white", bg=self.config["bg_color"], font=(self.config["font_family"], 14, "bold"))
        self.info_label.grid(row=0, column=0, columnspan=2, pady=10)
        
        self.setup_ui()
        self.start_new_game()

    def create_menu(self):
        menubar = tk.Menu(self.root)
        game_menu = tk.Menu(menubar, tearoff=0)
        game_menu.add_command(label="Новая игра", command=self.start_new_game)
        game_menu.add_command(label="Настройки", command=self.open_settings)
        game_menu.add_command(label="Таблица рекордов", command=self.open_highscores)
        game_menu.add_separator()
        game_menu.add_command(label="Выход", command=self.root.quit)
        menubar.add_cascade(label="Меню", menu=game_menu)
        self.root.config(menu=menubar)

    def setup_ui(self):
        font_fmt = (self.config["font_family"], self.config["font_size"])
        
        self.left_frame = tk.LabelFrame(self.main_frame, text="Ваше Поле", bg=self.config["bg_color"], fg="white", font=font_fmt)
        self.left_frame.grid(row=1, column=0, padx=20, pady=10)
        
        self.right_frame = tk.LabelFrame(self.main_frame, text="Поле Противника", bg=self.config["bg_color"], fg="white", font=font_fmt)
        self.right_frame.grid(row=1, column=1, padx=20, pady=10)
        
        self.render_grids()

    def render_grids(self):
        for btn in list(self.left_buttons.values()) + list(self.right_buttons.values()):
            btn.destroy()
        self.left_buttons.clear()
        self.right_buttons.clear()

        grid_color = self.config.get("grid_color", "#34495e")
        for r in range(10):
            for c in range(10):
                btn_l = tk.Button(self.left_frame, width=3, height=1, bg=grid_color, activebackground=grid_color)
                btn_l.grid(row=r, column=c, padx=1, pady=1)
                self.left_buttons[(r, c)] = btn_l
                
                btn_r = tk.Button(self.right_frame, width=3, height=1, bg=grid_color, activebackground=grid_color)
                btn_r.grid(row=r, column=c, padx=1, pady=1)
                btn_r.config(command=lambda row=r, col=c: self.player_shoot(row, col))
                self.right_buttons[(r, c)] = btn_r

    def start_new_game(self):
        for timer_id in self.active_timers:
            try:
                self.root.after_cancel(timer_id)
            except:
                pass
        self.active_timers.clear()

        self.game_over = False
        self.actions_blocked = False
        self.current_turn = 1
        self.ai_targets = []
        
        self.board1 = [[0 for _ in range(10)] for _ in range(10)]
        self.board2 = [[0 for _ in range(10)] for _ in range(10)]
        self.shots1 = [[0 for _ in range(10)] for _ in range(10)]
        self.shots2 = [[0 for _ in range(10)] for _ in range(10)]
        
        self.place_ships_safely(self.board1)
        self.place_ships_safely(self.board2)
        
        if self.config.get("game_mode") == "Hotseat":
            self.show_screen_blanker("Игра НАЧИНАЕТСЯ! Ход Игрока 1. Нажмите для старта.", self.update_view)
        else:
            self.update_view()

    def place_ships_safely(self, board):
        ships_list = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]
        global_attempts = 0
        success = False
        
        while not success and global_attempts < 100:
            global_attempts += 1
            for r in range(10):
                for c in range(10):
                    board[r][c] = 0
                    
            success = True
            for ship in ships_list:
                placed = False
                attempts = 0
                while not placed:
                    attempts += 1
                    if attempts > 200:  
                        success = False
                        break
                    orient = random.choice(["H", "V"])
                    r = random.randint(0, 9)
                    c = random.randint(0, 9)
                    if self.can_place(board, r, c, ship, orient):
                        for i in range(ship):
                            if orient == "H":
                                board[r][c+i] = 1
                            else:
                                board[r+i][c] = 1
                        placed = True
                if not success:
                    break

    def can_place(self, board, r, c, length, orient):
        for i in range(length):
            curr_r = r + (i if orient == "V" else 0)
            curr_c = c + (i if orient == "H" else 0)
            if curr_r > 9 or curr_c > 9:
                return False
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    nr, nc = curr_r + dr, curr_c + dc
                    if 0 <= nr < 10 and 0 <= nc < 10:
                        if board[nr][nc] != 0:
                            return False
        return True

    def show_screen_blanker(self, message, next_step_callback):
        self.actions_blocked = True  
        blanker = tk.Toplevel(self.root)
        blanker.title("Передача хода")
        blanker.geometry(self.config.get("window_size", "900x650"))
        blanker.configure(bg="#1a252f")
        blanker.grab_set()
        
        blanker.protocol("WM_DELETE_WINDOW", lambda: None)

        lbl = tk.Label(blanker, text=message, fg="#e74c3c", bg="#1a252f", font=("Arial", 16, "bold"), wraplength=500)
        lbl.pack(expand=True)
        
        def close_blanker():
            self.actions_blocked = False  
            blanker.destroy()
            next_step_callback()

        btn = tk.Button(blanker, text="Я готов, показать поле", font=("Arial", 12), command=close_blanker, bg="#2ecc71", fg="white", padx=10, pady=5)
        btn.pack(pady=40)

    def update_view(self):
        is_hotseat = self.config.get("game_mode") == "Hotseat"
        grid_color = self.config["grid_color"]
        
        if is_hotseat:
            self.info_label.config(text=f"ХОДИТ: ИГРОК {self.current_turn}")
            self.left_frame.config(text=f"Поле Игрока {self.current_turn} (Ваш флот)")
            self.right_frame.config(text=f"Поле оппонента (Сюда стрелять)")
            
            current_board = self.board1 if self.current_turn == 1 else self.board2
            my_shots_at_enemy = self.shots1 if self.current_turn == 1 else self.shots2
            enemy_shots_at_me = self.shots2 if self.current_turn == 1 else self.shots1
        else:
            self.info_label.config(text="ИГРА ПРОТИВ КОМПЬЮТЕРА")
            self.left_frame.config(text="Ваш флот")
            self.right_frame.config(text="Флот Компьютера")
            
            current_board = self.board1
            my_shots_at_enemy = self.shots1
            enemy_shots_at_me = self.shots2

        for (r, c), btn in self.left_buttons.items():
            btn.config(state="disabled")
            if current_board[r][c] == 1:
                btn.config(bg="#2ecc71")  
            else:
                btn.config(bg=grid_color)
                
            if enemy_shots_at_me[r][c] == 1:
                btn.config(bg="#7f8c8d", text="•")  
            elif enemy_shots_at_me[r][c] == 2:
                btn.config(bg="#c0392b", text="X")
            else:
                btn.config(text="")

        for (r, c), btn in self.right_buttons.items():
            if self.actions_blocked:
                state_val = "disabled"
            else:
                state_val = "normal" if my_shots_at_enemy[r][c] == 0 else "disabled"

            if my_shots_at_enemy[r][c] == 0:
                btn.config(bg=grid_color, text="", state=state_val)
            elif my_shots_at_enemy[r][c] == 1:
                btn.config(bg="#95a5a6", text="•", state="disabled")
            elif my_shots_at_enemy[r][c] == 2:
                btn.config(bg="#e74c3c", text="X", state="disabled")

    def find_entire_ship(self, board, r, c):
        ship_cells = []
        queue = [(r, c)]
        visited = set(queue)
        
        while queue:
            curr_r, curr_c = queue.pop(0)
            ship_cells.append((curr_r, curr_c))
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = curr_r + dr, curr_c + dc
                if 0 <= nr < 10 and 0 <= nc < 10:
                    if board[nr][nc] == 1 and (nr, nc) not in visited:
                        visited.add((nr, nc))
                        queue.append((nr, nc))
        return ship_cells

    def check_and_mark_sunk(self, board, shots, r, c):
        ship_cells = self.find_entire_ship(board, r, c)
        
        if any(shots[sr][sc] != 2 for sr, sc in ship_cells):
            return False
            
        for sr, sc in ship_cells:
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    nr, nc = sr + dr, sc + dc
                    if 0 <= nr < 10 and 0 <= nc < 10:
                        if shots[nr][nc] == 0:
                            shots[nr][nc] = 1
        return True

    def player_shoot(self, r, c):
        if self.game_over or self.actions_blocked:
            return
            
        is_hotseat = self.config.get("game_mode") == "Hotseat"
        enemy_board = self.board2 if self.current_turn == 1 else self.board1
        my_shots = self.shots1 if self.current_turn == 1 else self.shots2
        
        if my_shots[r][c] != 0:
            return

        if enemy_board[r][c] == 1:
            my_shots[r][c] = 2  
            self.check_and_mark_sunk(enemy_board, my_shots, r, c)
            self.update_view()
            
            if self.check_win(enemy_board, my_shots):
                winner_id = self.current_turn if is_hotseat else 1
                self.end_game("player", winner_id)
                return
        else:
            my_shots[r][c] = 1  
            self.actions_blocked = True  
            self.update_view() 
            
            if is_hotseat:
                self.current_turn = 2 if self.current_turn == 1 else 1
                t_id = self.root.after(600, lambda: self.show_screen_blanker(
                    f"ПРОМАХ! Передайте управление Игроку {self.current_turn}.\nУбедитесь, что прошлый игрок отвернулся от экрана!", 
                    self.update_view
                ))
                self.active_timers.append(t_id)
            else:
                t_id = self.root.after(600, self.comp_shoot)
                self.active_timers.append(t_id)

    def comp_shoot(self):
        if self.game_over:
            return
        
        self.active_timers.clear()
        
        r, c = -1, -1
        difficulty = self.config.get("difficulty", "Normal")
        
        if difficulty == "Normal" and self.ai_targets:
            valid_targets = []
            for tr, tc in self.ai_targets:
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nr, nc = tr + dr, tc + dc
                    if 0 <= nr < 10 and 0 <= nc < 10 and self.shots2[nr][nc] == 0:
                        valid_targets.append((nr, nc))
            
            if valid_targets:
                r, c = random.choice(valid_targets)

        if r == -1 or c == -1:
            available_cells = [(row, col) for row in range(10) for col in range(10) if self.shots2[row][col] == 0]
            if not available_cells:
                self.actions_blocked = False
                return
            r, c = random.choice(available_cells)

        if self.board1[r][c] == 1:
            self.shots2[r][c] = 2
            if difficulty == "Normal":
                self.ai_targets.append((r, c))
                
            if self.check_and_mark_sunk(self.board1, self.shots2, r, c):
                if difficulty == "Normal":
                    sunk_cells = self.find_entire_ship(self.board1, r, c)
                    self.ai_targets = [cell for cell in self.ai_targets if cell not in sunk_cells]

            self.update_view()
            
            if self.check_win(self.board1, self.shots2):
                self.end_game("computer")
                return
                
            if not self.game_over:
                t_id = self.root.after(600, self.comp_shoot)  
                self.active_timers.append(t_id)
        else:
            self.shots2[r][c] = 1
            self.actions_blocked = False  
            self.update_view()

    def check_win(self, board, shots):
        for r in range(10):
            for c in range(10):
                if board[r][c] == 1 and shots[r][c] != 2:
                    return False
        return True

    def end_game(self, winner_type, winner_id=1):
        self.game_over = True
        self.actions_blocked = True  
        
        for timer_id in self.active_timers:
            try:
                self.root.after_cancel(timer_id)
            except:
                pass
        self.active_timers.clear()
        
        if winner_type == "computer":
            msg = "Компьютер победил!"
            winner_name = "Computer"
        else:
            winner_name = f"Игрок {winner_id}"
            msg = f"Победа! {winner_name} уничтожил весь флот!"
            
        messagebox.showinfo("Конец игры", msg)
        self.save_score(winner_name)

    def save_score(self, winner_name):
        updated = False
        for entry in self.scores:
            if entry["name"] == winner_name:
                entry["wins"] += 1
                updated = True
                break
        if not updated:
            self.scores.append({"name": winner_name, "wins": 1})
        save_json(SCORES_FILE, self.scores)

    def open_settings(self):
        settings_win = tk.Toplevel(self.root)
        settings_win.title("Настройки")
        settings_win.geometry("380x380")
        settings_win.grab_set()
        
        tk.Label(settings_win, text="Режим игры:").pack(pady=5)
        mode_combo = ttk.Combobox(settings_win, values=["vs Computer", "Hotseat"], state="readonly")
        mode_combo.set(self.config.get("game_mode", "vs Computer"))
        mode_combo.pack()

        tk.Label(settings_win, text="Сложность ИИ (против ПК):").pack(pady=5)
        diff_combo = ttk.Combobox(settings_win, values=["Easy", "Normal"], state="readonly")
        diff_combo.set(self.config["difficulty"])
        diff_combo.pack()

        tk.Label(settings_win, text="Размер окна:").pack(pady=5)
        size_combo = ttk.Combobox(settings_win, values=["800x600", "900x650", "1000x750"], state="readonly")
        size_combo.set(self.config["window_size"])
        size_combo.pack()
        
        tk.Label(settings_win, text="Цвет темы:").pack(pady=5)
        color_combo = ttk.Combobox(settings_win, values=["#2c3e50", "#16a085", "#2980b9"], state="readonly")
        color_combo.set(self.config["bg_color"])
        color_combo.pack()

        def save_and_close():
            self.config["game_mode"] = mode_combo.get()
            self.config["difficulty"] = diff_combo.get()
            self.config["window_size"] = size_combo.get()
            self.config["bg_color"] = color_combo.get()
            save_json(CONFIG_FILE, self.config)
            
            self.root.geometry(self.config["window_size"])
            self.root.configure(bg=self.config["bg_color"])
            self.main_frame.config(bg=self.config["bg_color"])
            self.info_label.config(bg=self.config["bg_color"])
            self.left_frame.config(bg=self.config["bg_color"])
            self.right_frame.config(bg=self.config["bg_color"])
            
            self.render_grids()  
            messagebox.showinfo("Успех", "Настройки сохранены! Начните Новую игру для применения изменений сетки.")
            settings_win.destroy()
            self.update_view()

        tk.Button(settings_win, text="Сохранить и Применить", command=save_and_close, bg="#2ecc71", fg="white").pack(pady=25)

    def open_highscores(self):
        score_win = tk.Toplevel(self.root)
        score_win.title("Таблица рекордов")
        score_win.geometry("320x300")
        
        sorted_scores = sorted(self.scores, key=lambda x: x["wins"], reverse=True)
        
        tk.Label(score_win, text="Топ игроков", font=("Arial", 14, "bold")).pack(pady=10)
        for idx, entry in enumerate(sorted_scores, 1):
            tk.Label(score_win, text=f"{idx}. {entry['name']} — Побед: {entry['wins']}").pack(pady=4)

if __name__ == '__main__':
    root = tk.Tk()
    app = BattleshipGame(root)
    root.mainloop()
