import math

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Расчет расстояния между двумя точками (в милях) по формуле гаверсинусов."""
    R = 3959.0
    d_lat = math.radians(lat2 - lat1)
    d_long = math.radians(lon2 - lon1)
    a = (math.sin(d_lat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(d_long / 2) ** 2)
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
    """Многокритериальный поиск рынков с учетом точного регистра полей из CSV."""
    filtered = []
    for m in markets:
        if city and city.lower() not in m.get('city', '').lower():
            continue
        if state and state.lower() not in m.get('state', '').lower():
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
    """Распределение рынков по различным критериям (рейтинг, локация, дистанция)."""
    if criteria == 'rating':
        return sorted(markets_list, key=lambda m: m.get('_avg_rating', 0.0), reverse=reverse)
    elif criteria == 'city_state':
        return sorted(markets_list, key=lambda m: (m.get('state', '').lower(), m.get('city', '').lower()),
                      reverse=reverse)
    elif criteria == 'distance':
        return sorted(markets_list,
                      key=lambda m: m.get('_distance') if m.get('_distance') is not None else float('inf'),
                      reverse=reverse)
    else:
        return sorted(markets_list, key=lambda m: m.get('MarketName', '').lower(), reverse=reverse)

def delete_market_by_id(markets: list[dict], fmid: str) -> list[dict]:
    return list(filter(lambda m: m.get('FMID') != fmid, markets))

def add_review_fp(reviews: list[dict], fmid: str, first_name: str, last_name: str, rating: int, text: str) -> list[dict]:
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
    print("ЗАПУСК ВСТРОЕННЫХ ТЕСТОВ ЯДРА CORE.PY...")
    mock_markets = [
        {
            'FMID': '1001', 'MarketName': 'Downtown Market',
            'city': 'Los Angeles', 'state': 'California', 'zip': '90001',
            'y': '34.0522', 'x': '-118.2437'
        },
        {
            'FMID': '1002', 'MarketName': 'Bay Area Fresh',
            'city': 'San Francisco', 'state': 'California', 'zip': '94105',
            'y': '37.7749', 'x': '-122.4194'
        }
    ]
    mock_reviews = [{'fmid': '1001', 'first_name': 'John', 'last_name': 'Doe', 'rating': 5, 'text': 'Great!'}]
    
    assert 345.0 < calculate_distance(34.0522, -118.2437, 37.7749, -122.4194) < 350.0
    assert get_market_rating_info('1001', mock_reviews) == (5.0, 1)
    assert len(search_markets(mock_markets, mock_reviews, state="California")) == 2
    assert len(delete_market_by_id(mock_markets, '1002')) == 1
    print("УСПЕХ: Все встроенные ассерты ядра успешно пройдены!")
    print("============================================================\n")
