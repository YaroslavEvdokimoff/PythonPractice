import sys
import os

# Автоматически определяем корень проекта, чтобы путь к CSV всегда работал
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, "data", "Export.csv")
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from io_handler import load_csv_data
    import core
except ImportError as e:
    print(f"[Критическая ошибка импорта]: Не удалось загрузить соседние модули. {e}")
    sys.exit(1)


def print_help():
    print("\n=== Главное меню команд ===")
    print("  list              - Просмотр списка всех рынков страны (с пагинацией)")
    print("  search            - Поиск по городу/штату/индексу (+ ограничение в милях)")
    print("  delete <FMID>     - Удалить фермерский рынок по его ID (FMID)")
    print("  help              - Показать это меню")
    print("  exit              - Выйти из программы")


def display_market_details(market: dict, reviews: list[dict]):
    """Просмотр подробных данных о рынке и его рецензиях (Пункт 6 ТЗ)."""
    print("\n" + "=" * 60)
    print(f"КАРТОЧКА РЫНКА: {market.get('MarketName')}")
    print("=" * 60)
    print(f"Уникальный ID (FMID): {market.get('FMID')}")
    print(f"Штат: {market.get('State')} | Город: {market.get('City')} | Индекс: {market.get('zip')}")
    print(f"Улица: {market.get('street', 'Не указана')}")
    print(f"Гео-координаты: Широта {market.get('y')} / Долгота {market.get('x')}")

    if '_distance' in market and market['_distance'] is not None:
        print(f"Удаленность от вашей точки поиска: {round(market['_distance'], 2)} миль")

    avg_rating, count = core.get_market_rating_info(market.get('FMID'), reviews)
    print(f"Текущий рейтинг: ★ {avg_rating} (Всего рецензий: {count})")
    print("-" * 60)
    print("РЕЦЕНЗИИ И ОТЗЫВЫ:")

    market_reviews = list(filter(lambda r: r['fmid'] == market.get('FMID'), reviews))
    if not market_reviews:
        print("  Рецензий пока нет. Вы можете оставить первую!")
    else:
        for r in market_reviews:
            print(f"  Пользователь: {r['first_name']} {r['last_name']}")
            print(f"  Оценка: {'★' * r['rating']} ({r['rating']}/5)")
            if r['text']:
                print(f"  Текст: {r['text']}")
            print("  " + "-" * 30)

    print("\nДоступные действия в карточке:")
    print("  1 - Оставить рецензию (Рейтинг + Имя/Фамилия)")
    print("  0 - Вернуться назад к списку выдачи")
    return input("Выберите действие: ").strip()


def handle_market_interaction(market: dict, reviews: list[dict]) -> list[dict]:
    """Интерактивное добавление рецензии, привязанной к ФИО."""
    current_reviews = reviews
    while True:
        choice = display_market_details(market, current_reviews)
        if choice == '1':
            print("\n--- Форма добавления рецензии ---")
            first_name = input("Введите ваше Имя (Обязательно): ").strip()
            last_name = input("Введите вашу Фамилию (Обязательно): ").strip()

            if not first_name or not last_name:
                print("Ошибка: Рецензия должна быть строго привязана к имени и фамилии!")
                continue

            try:
                rating = int(input("Поставьте рейтинг (обязательно от 1 до 5 звезд): ").strip())
                if not (1 <= rating <= 5):
                    print("Ошибка: Рейтинг принимает значения только от 1 до 5!")
                    continue
            except ValueError:
                print("Ошибка: Рейтинг должен быть целым числом!")
                continue

            text = input("Текст отзыва (необязательно, нажмите Enter для пропуска): ").strip()

            # Обновляем список отзывов (ФП-стиль)
            current_reviews = core.add_review_fp(current_reviews, market.get('FMID'), first_name, last_name, rating,
                                                 text)
            print("Спасибо! Ваша рецензия успешно добавлена.")
        elif choice == '0':
            break
    return current_reviews


def handle_list_and_sorting(markets_to_show: list[dict], reviews: list[dict]) -> tuple[list[dict], list[dict]]:
    """Постраничный вывод списков с возможностью распределения (sort) и перехода к деталям (view)."""
    page = 1
    per_page = 5
    current_list = markets_to_show
    current_reviews = reviews

    while True:
        # Динамически обновляем средний рейтинг перед рендерингом страницы
        for m in current_list:
            avg_r, _ = core.get_market_rating_info(m.get('FMID'), current_reviews)
            m['_avg_rating'] = avg_r

        total = len(current_list)
        total_pages = max(1, (total + per_page - 1) // per_page)
        start_idx = (page - 1) * per_page
        page_items = current_list[start_idx:start_idx + per_page]

        print(f"\n" + "=" * 15 + f" СТРАНИЦА {page} из {total_pages} (Всего найдено: {total}) " + "=" * 15)
        for idx, market in enumerate(page_items):
            dist_str = f" | Удаленность: {round(market['_distance'], 1)} миль" if market.get(
                '_distance') is not None else ""
            print(f" [{idx + 1}] {market.get('MarketName')}")
            print(f"     ID (FMID): {market.get('FMID')}")
            print(f"     Локация: {market.get('City')}, {market.get('State')}, Zip: {market.get('zip')}{dist_str}")
            print(f"     Средний рейтинг: ★ {market.get('_avg_rating', 0.0)}")
            print("-" * 65)

        print("\nКоманды управления списком:")
        print("  N - Следующая страница  |  P - Предыдущая страница")
        print("  view <номер>            - Перейти к подробным данным рынка (например: view 1)")
        print("  sort                    - Распределить (отсортировать) этот список по критериям")
        print("  B                       - Вернуться в Главное меню")

        choice = input("Введите команду: ").strip().lower()

        if choice == 'n':
            if (page * per_page) < total:
                page += 1
            else:
                print("Вы на последней странице.")
        elif choice == 'p':
            if page > 1:
                page -= 1
            else:
                print("Вы на первой странице.")
        elif choice.startswith('view '):
            try:
                item_idx = int(choice.split()[1]) - 1
                if 0 <= item_idx < len(page_items):
                    selected_market = page_items[item_idx]
                    current_reviews = handle_market_interaction(selected_market, current_reviews)
                else:
                    print("Ошибка: Нет рынка под таким номером на текущей странице!")
            except (ValueError, IndexError):
                print("Неверный формат. Используйте строго: view 1 (или другой номер от 1 до 5)")
        elif choice == 'sort':
            print("\nВыберите критерий распределения (сортировки):")
            print("  1 - По рейтингу")
            print("  2 - По городу и штату")
            print("  3 - По удаленности (работает, если задавались мили при поиске)")
            crit_choice = input("Критерий (1-3): ").strip()

            crit_map = {'1': 'rating', '2': 'city_state', '3': 'distance'}
            criteria = crit_map.get(crit_choice, 'name')

            print("\nУкажите направление распределения:")
            print("  1 - От Максимального к Минимальному (по убыванию)")
            print("  2 - От Минимального к Максимальному (по возрастанию)")
            direction = input("Направление (1-2): ").strip()

            reverse_flag = True if direction == '1' else False

            current_list = core.sort_markets(current_list, criteria, reverse=reverse_flag)
            page = 1  # Сбрасываем пагинацию на первую страницу
            print("Список успешно перераспределен по выбранному критерию!")
        elif choice == 'b':
            break

    return current_list, current_reviews


def main_repl_loop():
    print("=" * 60)
    print(" СИСТЕМА УПРАВЛЕНИЯ ФЕРМЕРСКИМИ РЫНКАМИ (ВЕРСИЯ 1: ФП + CLI)")
    print("=" * 60)
    print("Загрузка данных из CSV...")

    global_markets = load_csv_data(CSV_PATH)
    if not global_markets:
        global_markets = load_csv_data("Export.csv")

    if not global_markets:
        print(f"[Критическая ошибка]: Не удалось прочесть Export.csv по пути {CSV_PATH}")
        sys.exit(1)

    global_reviews = []
    print(f"Успешно загружено {len(global_markets)} фермерских рынков страны.")
    print_help()

    while True:
        try:
            raw_input = input("\nГлавный REPL> ").strip()
            if not raw_input:
                continue

            parts = raw_input.split(maxsplit=1)
            command = parts[0].lower()
            args = parts[1] if len(parts) > 1 else ""

            if command == 'exit':
                print("Выход из программы. До свидания!")
                break
            elif command == 'help':
                print_help()
            elif command == 'list':
                prepared_markets = core.search_markets(global_markets, global_reviews)
                _, global_reviews = handle_list_and_sorting(prepared_markets, global_reviews)
            elif command == 'search':
                print("\n--- Критерии текстового поиска (нажмите Enter для пропуска поля) ---")
                city = input("Город: ").strip()
                state = input("Штат (две буквы, например TX): ").strip()
                zip_code = input("Почтовый индекс (ZIP): ").strip()

                print("\n--- Фильтрация по удаленности зоны поиска ---")
                geo_opt = input("Ограничить зону поиска по дальности в милях? (y/n): ").strip().lower()

                c_lat, c_lon, max_d = None, None, None
                if geo_opt == 'y':
                    try:
                        c_lat = float(input("Введите широту (Latitude центра, например 42.36): ").strip())
                        c_lon = float(input("Введите долготу (Longitude центра, например -71.05): ").strip())
                        max_d = float(input("Введите максимальную дальность в милях (например 30): ").strip())
                    except ValueError:
                        print("Ошибка: Введены некорректные числа. Ограничение дальности пропущено.")

                results = core.search_markets(global_markets, global_reviews, city, state, zip_code, c_lat, c_lon,
                                              max_d)
                print(f"\nНайдено совпадений в поисковой выдаче: {len(results)}")

                if results:
                    if c_lat is not None:
                        results = core.sort_markets(results, 'distance', reverse=False)
                    _, global_reviews = handle_list_and_sorting(results, global_reviews)

            elif command == 'delete':
                if not args:
                    print("Ошибка: Укажите ID (FMID) для удаления. Пример: delete 100123")
                    continue
                before = len(global_markets)
                global_markets = core.delete_market_by_id(global_markets, args)
                if len(global_markets) == before:
                    print(f"Рынок с ID {args} не найден.")
                else:
                    print(f"Рынок с ID {args} успешно удален из текущей сессии программы.")
            else:
                print("Неизвестная команда. Введите 'help' для списка доступных действий.")

        except KeyboardInterrupt:
            print("\nДля выхода наберите команду 'exit'.")
        except Exception as e:
            print(f"Системная ошибка выполнения: {e}")


if __name__ == '__main__':
    main_repl_loop()
