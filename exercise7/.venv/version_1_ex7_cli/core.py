import math


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Расчет расстояния между двумя точками (в милях) по гаверсинусам."""
    R = 3959.0
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (math.sin(d_lat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(d_lon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def get_market_rating_info(fmid: str, reviews: list[dict]) -> tuple[float, int]:
    """Вычисляет средний рейтинг и количество отзывов для рынка."""
    market_reviews = list(filter(lambda r: r['fmid'] == fmid, reviews))
    if not market_reviews:
        return 0.0, 0
    ratings = list(map(lambda r: r['rating'], market_reviews))
    return round(sum(ratings) / len(ratings), 1), len(ratings)


def search_markets(markets: list[dict], reviews: list[dict],
                   city: str = "", state: str = "", zip_code: str = "",
                   center_lat: float = None, center_lon: float = None, max_miles: float = None) -> list[dict]:
    """Многокритериальный поиск рынков. Возвращает обогащенные копии словарей."""
    filtered = []
    for m in markets:
        if city and city.lower() not in m.get('City', '').lower():
            continue
        if state and state.lower() not in m.get('State', '').lower():
            continue
        if zip_code and zip_code.strip() != m.get('zip', '').strip():
            continue

        avg_rating, _ = get_market_rating_info(m.get('FMID'), reviews)
        distance = None

        if center_lat is not None and center_lon is not None:
            try:
                m_lat = float(m.get('y', 0))
                m_lon = float(m.get('x', 0))
                distance = calculate_distance(center_lat, center_lon, m_lat, m_lon)
                if max_miles is not None and distance > max_miles:
                    continue
            except (ValueError, TypeError):
                if max_miles is not None:
                    continue

        market_copy = m.copy()
        market_copy['_distance'] = distance
        market_copy['_avg_rating'] = avg_rating
        filtered.append(market_copy)
    return filtered


def sort_markets(markets_list: list[dict], criteria: str, reverse: bool = False) -> list[dict]:
    """
    Распределение рынков по различным критериям (Пункт 6).
    criteria: 'rating' (рейтинг), 'city_state' (город и штат), 'distance' (удаленность).
    """
    if criteria == 'rating':
        # Сортировка по рейтингу
        return sorted(markets_list, key=lambda m: m.get('_avg_rating', 0.0), reverse=reverse)
    elif criteria == 'city_state':
        # Сортировка по городу и штату одновременно
        return sorted(markets_list, key=lambda m: (m.get('State', '').lower(), m.get('City', '').lower()),
                      reverse=reverse)
    elif criteria == 'distance':
        # Сортировка по удаленности (рынки без координат уходят в конец)
        return sorted(markets_list,
                      key=lambda m: m.get('_distance') if m.get('_distance') is not None else float('inf'),
                      reverse=reverse)
    else:
        return sorted(markets_list, key=lambda m: m.get('MarketName', '').lower(), reverse=reverse)


def delete_market_by_id(markets: list[dict], fmid: str) -> list[dict]:
    return list(filter(lambda m: m.get('FMID') != fmid, markets))


def add_review_fp(reviews: list[dict], fmid: str, first_name: str, last_name: str, rating: int, text: str) -> list[
    dict]:
    """Создание рецензии, привязанной к имени и фамилии (ФП-стиль)."""
    new_review = {
        'fmid': fmid,
        'first_name': first_name,
        'last_name': last_name,
        'rating': rating,
        'text': text
    }
    return reviews + [new_review]



if __name__ == '__main__':
    print("ЗАПУСК МОДУЛЬНЫХ ТЕСТОВ")

    # 1. ПОДГОТОВКА ТЕСТОВЫХ ДАННЫХ
    mock_markets = [
        {
            'FMID': '1001', 'MarketName': 'Downtown Market',
            'City': 'Los Angeles', 'State': 'California', 'zip': '90001',
            'y': '34.0522', 'x': '-118.2437'  # Точные координаты LA
        },
        {
            'FMID': '1002', 'MarketName': 'Bay Area Fresh',
            'City': 'San Francisco', 'State': 'California', 'zip': '94105',
            'y': '37.7749', 'x': '-122.4194'  # Точные координаты SF
        },
        {
            'FMID': '1003', 'MarketName': 'Austin Farmers',
            'City': 'Austin', 'State': 'Texas', 'zip': '73301',
            'y': '30.2672', 'x': '-97.7431'   # Точные координаты Austin
        }
    ]

    mock_reviews = [
        {'fmid': '1001', 'first_name': 'John', 'last_name': 'Doe', 'rating': 5, 'text': 'Great!'},
        {'fmid': '1001', 'first_name': 'Jane', 'last_name': 'Smith', 'rating': 4, 'text': 'Nice.'},
        {'fmid': '1002', 'first_name': 'Bob', 'last_name': 'Jones', 'rating': 2, 'text': 'Bad.'}
    ]

    # 2. ТЕСТ: calculate_distance
    dist = calculate_distance(34.0522, -118.2437, 37.7749, -122.4194)
    assert 345.0 < dist < 350.0, f"Ошибка расчета расстояния: {dist}"

    # 3. ТЕСТ: get_market_rating_info
    avg_r, count_r = get_market_rating_info('1001', mock_reviews)
    assert avg_r == 4.5, f"Неверный средний рейтинг: {avg_r}"
    assert count_r == 2, f"Неверное кол-во отзывов: {count_r}"

    avg_r_empty, count_r_empty = get_market_rating_info('1003', mock_reviews)
    assert avg_r_empty == 0.0 and count_r_empty == 0, "Рынок без отзывов должен возвращать (0.0, 0)"

    # 4. ТЕСТ: search_markets
    # Поиск по критерию штата 'California'
    cali_results = search_markets(mock_markets, mock_reviews, state="California")
    assert len(cali_results) == 2, f"Должно быть найдено 2 рынка в Калифорнии, найдено {len(cali_results)}"

    # Поиск по радиусу: ищем в пределах 100 миль от центра Лос-Анджелеса
    geo_results = search_markets(mock_markets, mock_reviews, center_lat=34.0522, center_lon=-118.2437, max_miles=100.0)
    assert len(geo_results) == 1, "Должен быть найден только 1 рынок в радиусе 100 миль"
    assert geo_results[0]['FMID'] == '1001'

    # 5. ТЕСТ: sort_markets
    # Сортировка по рейтингу по убыванию (reverse=True)
    sorted_by_rating = sort_markets(cali_results, criteria='rating', reverse=True)
    assert sorted_by_rating[0]['FMID'] == '1001', "Первым должен идти рынок с наивысшим рейтингом"

    # 6. ТЕСТ: delete_market_by_id
    remaining_markets = delete_market_by_id(mock_markets, '1002')
    assert len(remaining_markets) == 2, "После удаления должно остаться 2 рынка"
    assert not any(m['FMID'] == '1002' for m in remaining_markets), "Рынок 1002 не должен присутствовать"

    # 7. ТЕСТ: add_review_fp
    updated_reviews = add_review_fp(mock_reviews, '1003', 'Alice', 'Green', 5, 'Perfect!')
    assert len(updated_reviews) == len(mock_reviews) + 1, "Новый список должен увеличиться на 1 элемент"
    assert len(mock_reviews) == 3, "Исходный список mock_reviews НЕ должен измениться (принцип ФП)"

    print("УСПЕХ: Все тесты core.py успешно пройдены!")
    print("============================================================\n")



