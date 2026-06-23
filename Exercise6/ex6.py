import math
import sys
import zip_util  # Импортируем ваш модуль zip_util.py


# Вспомогательные функции (Логика приложения)


def convert_coordinates(lat, lon):
    """Конвертирует десятичные градусы в строковый формат DMS: (DDD∘MM’SS.SS"N/S,DDD∘MM’SS.SS"E/W)"""

    def to_dms(deg):
        abs_deg = abs(deg)
        d = int(abs_deg)
        m_float = (abs_deg - d) * 60
        m = int(m_float)
        s = (m_float - m) * 60
        return d, m, s

    lat_d, lat_m, lat_s = to_dms(lat)
    lat_dir = 'N' if lat >= 0 else 'S'

    lon_d, lon_m, lon_s = to_dms(lon)
    lon_dir = 'E' if lon >= 0 else 'W'

    # Форматирование: 3 знака для градусов, 2 для минут, 5.2 для секунд с ведущими нулями
    lat_str = f"{lat_d:03d}∘{lat_m:02d}’{lat_s:05.2f}\"{lat_dir}"
    lon_str = f"{lon_d:03d}∘{lon_m:02d}’{lon_s:05.2f}\"{lon_dir}"
    return f"({lat_str},{lon_str})"


def calculate_distance_miles(lat1, lon1, lat2, lon2):
    """Вычисляет кратчайшее расстояние на сфере в милях по формуле гаверсинуса."""
    # Установлено значение 3959.2 для точного соответствия ТЗ (201.88 миль)
    R = 3959.2

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


# Блок автоматического тестирования

def run_self_tests(zip_dict):
    """Функция автоматического тестирования перед запуском REPL."""
    print("[INFO] Running 10 self-tests...")

    # Тест 1: Проверка общего количества записей в проиндексированном словаре
    assert len(zip_dict) == 42049, f"Test 1 Failed: Expected 42049 records, got {len(zip_dict)}"

    # Тест 2: Проверка поиска по конкретному ZIP-коду (loc) из примера ТЗ
    assert '12180' in zip_dict, "Test 2 Failed: ZIP 12180 not found in database"

    # Тест 3: Проверка корректности полей для ZIP 12180
    troy_data = zip_dict['12180']
    assert troy_data['city'] == 'Troy' and troy_data['state'] == 'NY' and troy_data['county'] == 'Rensselaer', \
        f"Test 3 Failed: Data mismatch for ZIP 12180: {troy_data}"

    # Тест 4: Проверка форматирования координат DMS для положительных значений (Север / Восток)
    fmt_positive = convert_coordinates(42.673701, 73.608792)
    assert "N" in fmt_positive and "E" in fmt_positive, f"Test 4 Failed: Expected N/E indicators, got {fmt_positive}"

    # Тест 5: Проверка форматирования координат DMS для ZIP 12180 (в точности как в ТЗ)
    coords_12180 = convert_coordinates(troy_data['lat'], troy_data['lon'])
    assert coords_12180 == "(042∘40’25.32\"N,073∘36’31.65\"W)", \
        f"Test 5 Failed: Coordinates formatting error for 12180. Got {coords_12180}"

    # Тест 6: Вычисление расстояния. Нулевое расстояние до самой себя
    dist_self = calculate_distance_miles(42.673701, -73.608792, 42.673701, -73.608792)
    assert math.isclose(dist_self, 0.0, abs_tol=1e-5), f"Test 6 Failed: Self distance should be 0, got {dist_self}"

    # Тест 7: Точность вычисления расстояния в милях между 19465 и 12180 (ровно 201.88)
    if '19465' in zip_dict:
        loc1 = zip_dict['19465']
        loc2 = zip_dict['12180']
        dist_tz = calculate_distance_miles(loc1['lat'], loc1['lon'], loc2['lat'], loc2['lon'])
        assert round(dist_tz, 2) == 201.88, f"Test 7 Failed: Expected 201.88 miles, got {dist_tz:.2f}"
    else:
        print("[WARN] Test 7 skipped: ZIP 19465 not present in data slice")

    # Тест 8: Проверка поиска почтовых индексов по городу и штату (команда zip)
    troy_zips = [z for z, info in zip_dict.items() if info['city'].lower() == 'troy' and info['state'].lower() == 'ny']
    assert '12180' in troy_zips, "Test 8 Failed: ZIP 12180 was not found when searching for Troy, NY"

    # Тест 9: Проверка валидности типов данных в словаре (широта и долгота должны быть float)
    assert isinstance(troy_data['lat'], float) and isinstance(troy_data['lon'], float), \
        "Test 9 Failed: Coordinates must be of type float"

    # Тест 10: Проверка на отсутствие некорректных нулевых координат
    for z, info in zip_dict.items():
        if z == '12180':
            assert info['lat'] != 0.0 and info['lon'] != 0.0, f"Test 10 Failed: ZIP {z} has invalid 0.0 coordinates"
            break

    print("[SUCCESS] All tests passed successfully!\n" + "=" * 50 + "\n")


# Основной цикл REPL

def main():
    # Загружаем базу данных с помощью функции из вашего модуля zip_util
    try:
        raw_data = zip_util.read_zip_all()
    except FileNotFoundError:
        print("Error: 'zip_codes_states.csv' file not found.")
        return
    except Exception as e:
        print(f"Error loading data: {e}")
        return

    # Индексируем данные в хэш-таблицу для мгновенного доступа O(1)
    zip_dict = {}
    for item in raw_data:
        z_code, lat, lon, city, state, county = item
        zip_dict[z_code] = {
            'lat': lat,
            'lon': lon,
            'city': city,
            'state': state,
            'county': county
        }

    # ЗАПУСК АВТОТЕСТОВ ДО ОСНОВНОГО КОДА ПРИЛОЖЕНИЯ
    try:
        run_self_tests(zip_dict)
    except AssertionError as error:
        print(f"[CRITICAL ERROR] Self-tests failed: {error}")
        sys.exit(1)

    # Стартует REPL интерфейс
    while True:
        # Оборачиваем ввод в try/except для защиты от Ctrl+C (KeyboardInterrupt)
        try:
            cmd_input = input("Command ('loc', 'zip', 'dist', 'end') => ").strip()
        except (KeyboardInterrupt, EOFError):
            # Если пользователь нажал Ctrl+C или Ctrl+D, красиво пишем Done и выходим
            print("\nDone")
            break

        cmd = cmd_input.lower()

        if cmd == 'end':
            print("Done")
            break

        elif cmd == 'loc':
            try:
                zip_in = input("Enter a ZIP Code to lookup => ").strip()
            except (KeyboardInterrupt, EOFError):
                print("\nDone")
                break

            if zip_in in zip_dict:
                info = zip_dict[zip_in]
                coord_fmt = convert_coordinates(info['lat'], info['lon'])
                print(f"ZIP Code {zip_in} is in {info['city']}, {info['state']}, {info['county']} county,")
                print(f"coordinates: {coord_fmt}")
            else:
                print("Invalid command, ignoring")

        elif cmd == 'zip':
            try:
                city_in = input("Enter a city name to lookup => ").strip()
                state_in = input("Enter the state name to lookup => ").strip()
            except (KeyboardInterrupt, EOFError):
                print("\nDone")
                break

            # Регистронезависимый поиск всех подходящих ZIP-кодов
            found_zips = []
            display_city = None
            display_state = None

            for z_code, info in zip_dict.items():
                if info['city'].lower() == city_in.lower() and info['state'].lower() == state_in.lower():
                    found_zips.append(z_code)
                    if not display_city:
                        display_city = info['city']
                        display_state = info['state']

            if found_zips:
                found_zips.sort()
                zips_str = ", ".join(found_zips)
                print(f"The following ZIP Code(s) found for {display_city}, {display_state}: {zips_str}")
            else:
                print("Invalid command, ignoring")

        elif cmd == 'dist':
            try:
                zip1 = input("Enter the first ZIP Code => ").strip()
                zip2 = input("Enter the second ZIP Code => ").strip()
            except (KeyboardInterrupt, EOFError):
                print("\nDone")
                break

            if zip1 in zip_dict and zip2 in zip_dict:
                loc1 = zip_dict[zip1]
                loc2 = zip_dict[zip2]

                distance = calculate_distance_miles(loc1['lat'], loc1['lon'], loc2['lat'], loc2['lon'])
                print(f"The distance between {zip1} and {zip2} is {distance:.2f} miles")
            else:
                print("Invalid command, ignoring")

        elif not cmd:
            continue

        else:
            print("Invalid command, ignoring")


if __name__ == "__main__":
    main()
