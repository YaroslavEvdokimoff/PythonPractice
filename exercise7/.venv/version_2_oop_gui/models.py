class User:
    """Класс-модель пользователя (Требование ООП)."""

    def __init__(self, db_id: int, first_name: str, last_name: str):
        self.db_id = db_id
        self.first_name = first_name
        self.last_name = last_name

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


class Review:
    """Класс-модель рецензии с обязательным рейтингом от 1 до 5 звезд."""

    def __init__(self, db_id: int, market_id: int, user: User, rating: int, review_text: str = "") -> None:
        self.db_id = db_id
        self.market_id = market_id
        self.user = user  # Ассоциация: объект класса User встроен внутрь отзыва
        self.rating = rating
        self.review_text = review_text


class Market:
    """Класс-модель фермерского рынка."""

    def __init__(self, db_id: int, fmid: str, market_name: str, street: str,
                 city: str, state: str, zip_code: str,
                 latitude: float = None, longitude: float = None) -> None:
        self.db_id = db_id
        self.fmid = fmid
        self.market_name = market_name
        self.street = street if street else "Не указана"
        self.city = city
        self.state = state
        self.zip_code = zip_code
        self.latitude = latitude
        self.longitude = longitude

        # Расчетные свойства (динамически заполняются репозиторием СУБД)
        self.distance: float = None
        self.avg_rating: float = 0.0
        self.reviews_count: int = 0
