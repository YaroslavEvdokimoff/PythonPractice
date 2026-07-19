import tkinter as tk
from tkinter import ttk, messagebox
from db_manager import DatabaseManager
from models import Market


class MarketAppGUI:
    def __init__(self, root: tk.Tk, db_manager: DatabaseManager):
        self.root = root
        self.db = db_manager

        # Настройки главного окна
        self.root.title("Управление фермерскими рынками (Версия 2: ООП + СУБД + GUI)")
        self.root.geometry("1000x650")
        self.root.minsize(900, 500)

        # Переменные состояния для пагинации, поиска и сортировки
        self.current_page = 1
        self.per_page = 15
        self.total_records = 0

        self.sort_by = "market_name"
        self.reverse_sort = False

        self._init_ui()
        self.load_data()

    def _init_ui(self):
        """Создает каркас интерфейса с использованием сеток (grid)."""
        # --- 1. Панель поиска и фильтрации (Сверху) ---
        search_frame = ttk.LabelFrame(self.root, text=" Фильтры поиска и гео-локации ", padding=10)
        search_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(search_frame, text="Город:").grid(row=0, column=0, sticky=tk.W, padx=2)
        self.ent_city = ttk.Entry(search_frame, width=15)
        self.ent_city.grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(search_frame, text="Штат:").grid(row=0, column=2, sticky=tk.W, padx=2)
        self.ent_state = ttk.Entry(search_frame, width=8)
        self.ent_state.grid(row=0, column=3, padx=5, pady=2)

        ttk.Label(search_frame, text="ZIP-индекс:").grid(row=0, column=4, sticky=tk.W, padx=2)
        self.ent_zip = ttk.Entry(search_frame, width=10)
        self.ent_zip.grid(row=0, column=5, padx=5, pady=2)

        # Поля гео-локации
        ttk.Label(search_frame, text="Широта (Lat):").grid(row=1, column=0, sticky=tk.W, padx=2)
        self.ent_lat = ttk.Entry(search_frame, width=15)
        self.ent_lat.grid(row=1, column=1, padx=5, pady=2)

        ttk.Label(search_frame, text="Долгота (Lon):").grid(row=1, column=2, sticky=tk.W, padx=2)
        self.ent_lon = ttk.Entry(search_frame, width=8)
        self.ent_lon.grid(row=1, column=3, padx=5, pady=2)

        ttk.Label(search_frame, text="Радиус (миль):").grid(row=1, column=4, sticky=tk.W, padx=2)
        self.ent_radius = ttk.Entry(search_frame, width=10)
        self.ent_radius.grid(row=1, column=5, padx=5, pady=2)

        btn_search = ttk.Button(search_frame, text="Поиск", command=self.action_search)
        btn_search.grid(row=0, column=6, rowspan=2, padx=15, sticky=tk.NSEW)

        btn_clear = ttk.Button(search_frame, text="Сбросить", command=self.action_reset)
        btn_clear.grid(row=0, column=7, rowspan=2, padx=5, sticky=tk.NSEW)

        # --- 2. Панель сортировки и управления (Посередине) ---
        ctrl_frame = ttk.Frame(self.root, padding=5)
        ctrl_frame.pack(fill=tk.X, padx=10)

        ttk.Label(ctrl_frame, text="Сортировка:").pack(side=tk.LEFT, padx=2)
        self.cmb_sort = ttk.Combobox(ctrl_frame,
                                     values=["По имени", "По рейтингу", "По городу/штату", "По удаленности"],
                                     state="readonly", width=15)
        self.cmb_sort.current(0)
        self.cmb_sort.pack(side=tk.LEFT, padx=5)
        self.cmb_sort.bind("<<ComboboxSelected>>", self.action_sort_changed)

        self.cmb_direction = ttk.Combobox(ctrl_frame, values=["Возрастание (Мин -> Макс)", "Убывание (Макс -> Мин)"],
                                          state="readonly", width=22)
        self.cmb_direction.current(0)
        self.cmb_direction.pack(side=tk.LEFT, padx=5)
        self.cmb_direction.bind("<<ComboboxSelected>>", self.action_sort_changed)

        btn_delete = ttk.Button(ctrl_frame, text="Удалить выбранный рынок", command=self.action_delete_market)
        btn_delete.pack(side=tk.RIGHT, padx=5)

        # --- 3. Главная таблица рынков (Treeview) ---
        table_frame = ttk.Frame(self.root, padding=10)
        table_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("fmid", "name", "location", "distance", "rating", "reviews")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")

        self.tree.heading("fmid", text="FMID")
        self.tree.heading("name", text="Название рынка")
        self.tree.heading("location", text="Локация (Город, Штат)")
        self.tree.heading("distance", text="Удаленность (миль)")
        self.tree.heading("rating", text="Рейтинг")
        self.tree.heading("reviews", text="Отзывы")

        self.tree.column("fmid", width=80, anchor=tk.CENTER)
        self.tree.column("name", width=250, anchor=tk.W)
        self.tree.column("location", width=180, anchor=tk.W)
        self.tree.column("distance", width=120, anchor=tk.CENTER)
        self.tree.column("rating", width=80, anchor=tk.CENTER)
        self.tree.column("reviews", width=80, anchor=tk.CENTER)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.bind("<Double-1>", self.action_open_market_details)

        # --- 4. Панель нижней навигации (Пагинатор) ---
        paginator_frame = ttk.Frame(self.root, padding=10)
        paginator_frame.pack(fill=tk.X)

        self.btn_prev = ttk.Button(paginator_frame, text="◀ Назад", command=self.action_prev_page)
        self.btn_prev.pack(side=tk.LEFT, padx=5)

        self.lbl_page_info = ttk.Label(paginator_frame, text="Страница 1 из 1 (Всего: 0)")
        self.lbl_page_info.pack(side=tk.LEFT, expand=True)

        self.btn_next = ttk.Button(paginator_frame, text="Вперед ▶", command=self.action_next_page)
        self.btn_next.pack(side=tk.RIGHT, padx=5)

    def load_data(self):
        """Извлекает страницу данных из СУБД с учетом фильтров и отправляет в таблицу."""
        # Чистим старые строки в таблице
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Считываем значения фильтров
        city = self.ent_city.get().strip()
        state = self.ent_state.get().strip()
        zip_code = self.ent_zip.get().strip()

        # Проверяем гео-координаты
        c_lat, c_lon, max_miles = None, None, None
        try:
            if self.ent_lat.get().strip() and self.ent_lon.get().strip():
                c_lat = float(self.ent_lat.get().strip())
                c_lon = float(self.ent_lon.get().strip())
                if self.ent_radius.get().strip():
                    max_miles = float(self.ent_radius.get().strip())
        except ValueError:
            messagebox.showerror("Ошибка ввода", "Широта, долгота и радиус должны быть числами!")
            return

        # Получаем данные из СУБД репозитория
        markets, self.total_records = self.db.get_markets_paginated(
            page=self.current_page, per_page=self.per_page,
            sort_by=self.sort_by, reverse=self.reverse_sort,
            city=city, state=state, zip_code=zip_code,
            c_lat=c_lat, c_lon=c_lon, max_miles=max_miles
        )

        # Отрисовываем строки Treeview
        # Отрисовываем строки Treeview (Исправлено сохранение объектов ООП)
        self.market_objects = {}  # Временный словарь для хранения связей ID -> Объект
        for m in markets:
            dist_val = f"{m.distance}" if m.distance is not None else "—"
            rating_val = f"★ {m.avg_rating}" if m.avg_rating > 0 else "—"

            item_id = self.tree.insert("", tk.END, iid=str(m.db_id), values=(
                m.fmid, m.market_name, f"{m.city}, {m.state}", dist_val, rating_val, m.reviews_count
            ))
            self.market_objects[str(m.db_id)] = m

        # Обновляем состояние кнопок пагинатора
        total_pages = max(1, (self.total_records + self.per_page - 1) // self.per_page)
        self.lbl_page_info.config(
            text=f"Страница {self.current_page} из {total_pages} (Всего найдено: {self.total_records})")

        self.btn_prev.config(state=tk.NORMAL if self.current_page > 1 else tk.DISABLED)
        self.btn_next.config(state=tk.NORMAL if self.current_page < total_pages else tk.DISABLED)

    def action_search(self):
        self.current_page = 1
        self.load_data()

    def action_reset(self):
        self.ent_city.delete(0, tk.END)
        self.ent_state.delete(0, tk.END)
        self.ent_zip.delete(0, tk.END)
        self.ent_lat.delete(0, tk.END)
        self.ent_lon.delete(0, tk.END)
        self.ent_radius.delete(0, tk.END)
        self.current_page = 1
        self.load_data()

    def action_prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.load_data()

    def action_next_page(self):
        total_pages = (self.total_records + self.per_page - 1) // self.per_page
        if self.current_page < total_pages:
            self.current_page += 1
            self.load_data()

    def action_sort_changed(self, event=None):
        crit_map = {
            "По имени": "market_name",
            "По рейтингу": "rating",
            "По городу/штату": "city_state",
            "По удаленности": "distance"
        }
        self.sort_by = crit_map.get(self.cmb_sort.get(), "market_name")
        self.reverse_sort = True if "Убывание" in self.cmb_direction.get() else False
        self.current_page = 1
        self.load_data()

    def action_delete_market(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Пожалуйста, выберите рынок из таблицы для удаления!")
            return

        market_id = int(selected[0])
        if messagebox.askyesno("Подтверждение",
                               "Вы уверены, что хотите безвозвратно удалить этот рынок и все связанные рецензии из СУБД?"):
            if self.db.delete_market(market_id):
                messagebox.showinfo("Успех", "Запись рынка успешно удалена каскадным методом.")
                self.load_data()

    def action_open_market_details(self, event):
        """Открывает диалоговое окно подробной карточки рынка."""
        selected = self.tree.selection()
        if not selected:
            return

        market_id_str = selected[0]
        target_market = self.market_objects.get(market_id_str)

        if target_market:
            MarketDetailsWindow(self.root, target_market, self.db, on_close_callback=self.load_data)


class MarketDetailsWindow(tk.Toplevel):
    """Окно детального просмотра карточки фермерского рынка (Пункт 6 ТЗ)."""

    def __init__(self, parent, market: Market, db_manager: DatabaseManager, on_close_callback):
        super().__init__(parent)
        self.market = market
        self.db = db_manager
        self.on_close_callback = on_close_callback

        self.title(f"Детали рынка: {market.market_name}")
        self.geometry("550x600")
        self.grab_set()  # Делаем окно модальным (блокирует главное окно до закрытия)

        self._init_ui()
        self.load_reviews()

    def _init_ui(self):
        # Панель параметров карточки
        info_frame = ttk.LabelFrame(self, text=" Сведения о фермерском рынке ", padding=10)
        info_frame.pack(fill=tk.X, padx=10, pady=5)

        labels = [
            f"Название: {self.market.market_name}",
            f"FMID: {self.market.fmid}",
            f"Адрес: {self.market.street}",
            f"Локация: {self.market.city}, {self.market.state}, {self.market.zip_code}",
            f"Координаты: {self.market.latitude or '—'} / {self.market.longitude or '—'}"
        ]
        if self.market.distance is not None:
            labels.append(f"Удаленность от центра поиска: {self.market.distance} миль")

        for i, text in enumerate(labels):
            ttk.Label(info_frame, text=text, font=("Arial", 10)).grid(row=i, column=0, sticky=tk.W, pady=2)

        # Лента рецензий пользователей
        review_frame = ttk.LabelFrame(self, text=" Рецензии и оценки пользователей ", padding=10)
        review_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.txt_reviews = tk.Text(review_frame, wrap=tk.WORD, state=tk.DISABLED, bg="#f9f9f9")
        self.txt_reviews.pack(fill=tk.BOTH, expand=True)

        # Форма добавления нового отзыва
        add_frame = ttk.LabelFrame(self, text=" Оставить новую рецензию ", padding=10)
        add_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(add_frame, text="Имя:").grid(row=0, column=0, sticky=tk.W)
        self.ent_fname = ttk.Entry(add_frame, width=15)
        self.ent_fname.grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(add_frame, text="Фамилия:").grid(row=0, column=2, sticky=tk.W)
        self.ent_lname = ttk.Entry(add_frame, width=15)
        self.ent_lname.grid(row=0, column=3, padx=5, pady=2)

        ttk.Label(add_frame, text="Рейтинг (1-5):").grid(row=1, column=0, sticky=tk.W)
        self.cmb_rating = ttk.Combobox(add_frame, values=["1", "2", "3", "4", "5"], state="readonly", width=5)
        self.cmb_rating.current(4)
        self.cmb_rating.grid(row=1, column=1, padx=5, pady=2, sticky=tk.W)

        ttk.Label(add_frame, text="Текст отзыва:").grid(row=2, column=0, sticky=tk.W)
        self.ent_text = ttk.Entry(add_frame, width=40)
        self.ent_text.grid(row=2, column=1, columnspan=3, padx=5, pady=2, sticky=tk.W)

        btn_submit = ttk.Button(add_frame, text="Отправить рецензию", command=self.action_submit_review)
        btn_submit.grid(row=3, column=0, columnspan=4, pady=5)

    def load_reviews(self):
        """Вычитывает список объектов рецензий из СУБД и форматирует текстовое поле карточки."""
        m_id = self.market.market_id if hasattr(self.market, 'market_id') else self.market.db_id
        reviews = self.db.get_market_reviews(m_id)

        self.txt_reviews.config(state=tk.NORMAL)
        self.txt_reviews.delete("1.0", tk.END)

        if not reviews:
            self.txt_reviews.insert(tk.END, "Отзывов на этот рынок пока нет. Будьте первым!")
        else:
            for r in reviews:
                stars = "★" * r.rating
                self.txt_reviews.insert(tk.END, f"[{r.user.full_name}] Оценка: {stars} ({r.rating}/5)\n")
                if r.review_text:
                    self.txt_reviews.insert(tk.END, f"Комментарий: {r.review_text}\n")
                self.txt_reviews.insert(tk.END, "-" * 40 + "\n")

        self.txt_reviews.config(state=tk.DISABLED)

    def action_submit_review(self):
        fname = self.ent_fname.get().strip()
        lname = self.ent_lname.get().strip()
        rating = int(self.cmb_rating.get())
        text = self.ent_text.get().strip()

        if not fname or not lname:
            messagebox.showerror("Ошибка", "Поля Имя и Фамилия обязательны для создания рецензии!")
            return

        m_id = self.market.market_id if hasattr(self.market, 'market_id') else self.market.db_id
        self.db.add_review(m_id, fname, lname, rating, text)

        messagebox.showinfo("Успех", "Ваша рецензия успешно добавлена в СУБД!")
        self.ent_fname.delete(0, tk.END)
        self.ent_lname.delete(0, tk.END)
        self.ent_text.delete(0, tk.END)

        self.load_reviews()
        self.on_close_callback()  # Обновляем состояние таблицы в главном окне

