import math
import unittest

class RatNum:
    """
    Абстрактная структура данных для представления неизменяемых рациональных чисел.

    Representation fields:
        _num: int - числитель дроби.
        _den: int - знаменатель дроби.

    Representation invariant (RI):
        Если объект является NaN: _num == 0 и _den == 0.
        Если объект корректен: _den > 0 и self.gcd(abs(_num), _den) == 1.

    Abstraction function (AF):
        Если _den == 0, то объект представляет специальный элемент "NaN".
        Если _den > 0, то объект представляет рациональное число _num / _den.
    """
    
    NaN = None 

    def __init__(self, num: int, den: int = 1):
        """
        Краткое описание: Конструктор рационального числа.
        Поля представления: _num (int) - числитель, _den (int) - знаменатель.
        Инвариант представления: _den >= 0; если _den == 0, то _num == 0; если _den > 0, то gcd(abs(_num), _den) == 1.
        Функция абстракции: Если _den == 0, представляет NaN. Иначе представляет число _num / _den.
        @requires: num, den — целые числа.
        @modifies: self
        @effects: Создает новое рациональное число в каноническом (сокращенном) виде.
        @throws: None
        @returns: None
        """
        if not isinstance(num, int) or not isinstance(den, int):
            raise TypeError("num and den must be integers")
        if den == 0:
            self._num = 0
            self._den = 0
        elif num == 0:
            self._num = 0
            self._den = 1
        else:
            g = math.gcd(abs(num), abs(den))
            sign = 1 if (num > 0 and den > 0) or (num < 0 and den < 0) else -1
            self._num = sign * (abs(num) // g)
            self._den = abs(den) // g

    @classmethod
    def _create_nan(cls):
        obj = cls.__new__(cls)
        obj._num = 0
        obj._den = 0
        return obj

    def is_nan(self) -> bool:
        """
        Краткое описание: Проверка на NaN.
        Поля представления: _num, _den
        Инвариант представления: см. канонический инвариант RatNum.
        Функция абстракции: см. функцию абстракции RatNum.
        @requires: None
        @modifies: None
        @effects: Проверяет, является ли число неопределенностью (NaN).
        @throws: None
        @returns: True, если self представляет NaN, иначе False.
        """
        return self._den == 0

    def is_negative(self) -> bool:
        """
        Краткое описание: Проверка на отрицательность.
        Поля представления: _num, _den
        Инвариант представления: см. канонический инвариант RatNum.
        Функция абстракции: см. функцию абстракции RatNum.
        @requires: None
        @modifies: None
        @effects: Проверяет, является ли число строго меньшим нуля.
        @throws: None
        @returns: True, если self < 0 и не NaN, иначе False.
        """
        return not self.is_nan() and self._num < 0

    def is_positive(self) -> bool:
        """
        Краткое описание: Проверка на положительность.
        Поля представления: _num, _den
        Инвариант представления: см. канонический инвариант RatNum.
        Функция абстракции: см. функцию абстракции RatNum.
        @requires: None
        @modifies: None
        @effects: Проверяет, является ли число строго большим нуля.
        @throws: None
        @returns: True, если self > 0 и не NaN, иначе False.
        """
        return not self.is_nan() and self._num > 0

    def compare_to(self, other: 'RatNum') -> int:
        """
        Краткое описание: Сравнение двух рациональных чисел.
        Поля представления: _num, _den
        Инвариант представления: см. канонический инвариант RatNum.
        Функция абстракции: см. функцию абстракции RatNum.
        @requires: other != None и является экземпляром RatNum.
        @modifies: None
        @effects: Сравнивает текущее число с другим. NaN равен самому себе и больше любого числа.
        @throws: TypeError если other не является экземпляром RatNum.
        @returns: -1 если self < other, 0 если self == other, 1 если self > other.
        """
        if not isinstance(other, RatNum):
            raise TypeError("other must be a RatNum instance")
        if self.is_nan() and other.is_nan():
            return 0
        if self.is_nan():
            return 1
        if other.is_nan():
            return -1
        diff = self._num * other._den - other._num * self._den
        if diff < 0:
            return -1
        elif diff > 0:
            return 1
        return 0

    def float_value(self) -> float:
        """
        Краткое описание: Преобразование в float.
        Поля представления: _num, _den
        Инвариант представления: см. канонический инвариант RatNum.
        Функция абстракции: см. функцию абстракции RatNum.
        @requires: self не должен быть NaN.
        @modifies: None
        @effects: Вычисляет вещественное значение дроби.
        @throws: ValueError если self.is_nan() == True.
        @returns: Значение в формате float.
        """
        if self.is_nan():
            raise ValueError("Cannot convert NaN to float")
        return self._num / self._den

    def int_value(self) -> int:
        """
        Краткое описание: Преобразование в int с округлением вниз.
        Поля представления: _num, _den
        Инвариант представления: см. канонический инвариант RatNum.
        Функция абстракции: см. функцию абстракции RatNum.
        @requires: self не должен быть NaN.
        @modifies: None
        @effects: Преобразует дробь в целое число методом floor division.
        @throws: ValueError если self.is_nan() == True.
        @returns: Округленное вниз целое число.
        """
        if self.is_nan():
            raise ValueError("Cannot convert NaN to int")
        return self._num // self._den

    def __neg__(self) -> 'RatNum':
        """
        Краткое описание: Унарный минус.
        Поля представления: _num, _den
        Инвариант представления: см. канонический инвариант RatNum.
        Функция абстракции: см. функцию абстракции RatNum.
        @requires: None
        @modifies: None
        @effects: Вычисляет аддитивную инверсию числа.
        @throws: None
        @returns: Новый объект RatNum, равный -self.
        """
        if self.is_nan():
            return self
        return RatNum(-self._num, self._den)

    def __add__(self, other: 'RatNum') -> 'RatNum':
        """
        Краткое описание: Сложение чисел.
        Поля представления: _num, _den
        Инвариант представления: см. канонический инвариант RatNum.
        Функция абстракции: см. функцию абстракции RatNum.
        @requires: other != None
        @modifies: None
        @effects: Вычисляет сумму двух рациональных чисел.
        @throws: None
        @returns: Новый объект RatNum (сумма), либо NaN.
        """
        if self.is_nan() or other.is_nan():
            return RatNum._create_nan()
        new_num = self._num * other._den + other._num * self._den
        new_den = self._den * other._den
        return RatNum(new_num, new_den)

    def __sub__(self, other: 'RatNum') -> 'RatNum':
        """
        Краткое описание: Вычитание чисел.
        Поля представления: _num, _den
        Инвариант представления: см. канонический инвариант RatNum.
        Функция абстракции: см. функцию абстракции RatNum.
        @requires: other != None
        @modifies: None
        @effects: Вычисляет разность двух рациональных чисел.
        @throws: None
        @returns: Новый объект RatNum (разность), либо NaN.
        """
        return self + (-other)

    def __mul__(self, other: 'RatNum') -> 'RatNum':
        """
        Краткое описание: Умножение чисел.
        Поля представления: _num, _den
        Инвариант представления: см. канонический инвариант RatNum.
        Функция абстракции: см. функцию абстракции RatNum.
        @requires: other != None
        @modifies: None
        @effects: Вычисляет произведение двух рациональных чисел.
        @throws: None
        @returns: Новый объект RatNum (произведение), либо NaN.
        """
        if self.is_nan() or other.is_nan():
            return RatNum._create_nan()
        return RatNum(self._num * other._num, self._den * other._den)

    def __truediv__(self, other: 'RatNum') -> 'RatNum':
        """
        Краткое описание: Деление чисел.
        Поля представления: _num, _den
        Инвариант представления: см. канонический инвариант RatNum.
        Функция абстракции: см. функцию абстракции RatNum.
        @requires: other != None
        @modifies: None
        @effects: Вычисляет частное от деления self на other.
        @throws: None
        @returns: Новый RatNum (частное). Если деление на 0 или аргумент NaN, возвращает NaN.
        """
        if self.is_nan() or other.is_nan() or other._num == 0:
            return RatNum._create_nan()
        return RatNum(self._num * other._den, self._den * other._num)

    def gcd(self, other: 'RatNum') -> 'RatNum':
        """
        Краткое описание: Наибольший общий делитель (НОД).
        Поля представления: _num, _den
        Инвариант представления: см. канонический инвариант RatNum.
        Функция абстракции: см. функцию абстракции RatNum.
        @requires: other != None
        @modifies: None
        @effects: Вычисляет НОД двух рациональных чисел по каноническому правилу для дробей.
        @throws: None
        @returns: Новый RatNum, представляющий НОД. Если один из операндов NaN, результат NaN.
        """
        if self.is_nan() or other.is_nan():
            return RatNum._create_nan()
        if self._num == 0:
            return other
        if other._num == 0:
            return self
        common_num = math.gcd(self._num, other._num)
        common_den = (self._den * other._den) // math.gcd(self._den, other._den)
        return RatNum(common_num, common_den)

    def __str__(self) -> str:
        """
        Краткое описание: Строковое представление.
        Поля представления: _num, _den
        Инвариант представления: см. канонический инвариант RatNum.
        Функция абстракции: см. функцию абстракции RatNum.
        @requires: None
        @modifies: None
        @effects: Формирует строку вида "NaN", "числитель/знаменатель" или просто "числитель".
        @throws: None
        @returns: Строка (str).
        """
        if self.is_nan():
            return "NaN"
        if self._den == 1:
            return str(self._num)
        return f"{self._num}/{self._den}"

    def __hash__(self) -> int:
        """
        Краткое описание: Хэш-функция объекта.
        Поля представления: _num, _den
        Инвариант представления: см. канонический инвариант RatNum.
        Функция абстракции: см. функцию абстракции RatNum.
        @requires: None
        @modifies: None
        @effects: Вычисляет хэш-код на основе неизменяемых полей.
        @throws: None
        @returns: Целое число (int).
        """
        return hash((self._num, self._den))

    def __eq__(self, other) -> bool:
        """
        Краткое описание: Сравнение на структурное равенство.
        Поля представления: _num, _den
        Инвариант представления: см. канонический инвариант RatNum.
        Функция абстракции: см. функцию абстракции RatNum.
        @requires: None
        @modifies: None
        @effects: Проверяет эквивалентность двух объектов. NaN равен только NaN.
        @throws: None
        @returns: True, если объекты логически равны, иначе False.
        """
        if not isinstance(other, RatNum):
            return False
        if self.is_nan() and other.is_nan():
            return True
        return self._num == other._num and self._den == other._den

RatNum.NaN = RatNum(0, 0)


class RatPoly:
    """
    Абстрактная структура данных для представления полиномов с рациональными коэффициентами.

    Representation fields:
        _coeffs: list[RatNum] - список коэффициентов полинома, где индекс равен степени переменной x.

    Representation invariant (RI):
        _coeffs всегда содержит хотя бы один элемент (len(_coeffs) >= 1).
        Если полином является NaN, список _coeffs является пустым ([]).
        Если полином не NaN, ни один коэффициент в списке не равен NaN.
        Если степень полинома больше 0, старший коэффициент не равен нулю (_coeffs[-1] != RatNum(0)).

    Abstraction function (AF):
        Список коэффициентов [c0, c1, ..., cn] при условии не-NaN представляет
        математический полином P(x) = c0 + c1*x + c2*x^2 + ... + cn*x^n.
        Список [RatNum(0, 0)] представляет специальное состояние "NaN".
        """

    NaN = None

    def __init__(self, coeffs: list[RatNum] = None, is_nan: bool = False):
        """
        Краткое описание: Конструктор полинома.
        Поля представления: _coeffs (list[RatNum]) - список коэффициентов, _is_nan (bool) - флаг NaN.
        Инвариант представления: Если _is_nan == True, то _coeffs пуст. Иначе _coeffs содержит минимум 1 элемент, старший элемент не равен нулю (кроме нулевого полинома). Коэффициенты не могут быть NaN.
        Функция абстракции: Если _is_nan == True, представляет NaN-полином. Иначе представляет многочлен P(x) = c_0 + c_1*x + ... + c_n*x^n.
        @requires: coeffs — список объектов RatNum или None.
        @modifies: self
        @effects: Инициализирует полином, удаляя лишние старшие нули для сохранения инварианта.
        @throws: None
        @returns: None
        """
        if is_nan or (coeffs and any(c.is_nan() for c in coeffs)):
            self._is_nan = True
            self._coeffs = []
            return

        self._is_nan = False
        if not coeffs:
            self._coeffs = [RatNum(0)]
        else:
            idx = len(coeffs) - 1
            while idx > 0 and coeffs[idx] == RatNum(0):
                idx -= 1
            self._coeffs = [c for c in coeffs[:idx + 1]]

    @classmethod
    def _create_nan(cls):
        return cls(is_nan=True)

    def degree(self) -> int:
        """
        Краткое описание: Получение старшей степени полинома.
        Поля представления: _coeffs, _is_nan
        Инвариант представления: см. канонический инвариант RatPoly.
        Функция абстракции: см. функцию абстракции RatPoly.
        @requires: None
        @modifies: None
        @effects: Вычисляет степень полинома.
        @throws: None
        @returns: Степень полинома (int). Для нуля или NaN возвращает 0.
        """
        if self._is_nan:
            return 0
        return len(self._coeffs) - 1

    def get_coeff(self, degree: int) -> RatNum:
        """
        Краткое описание: Получение коэффициента при конкретной степени.
        Поля представления: _coeffs, _is_nan
        Инвариант представления: см. канонический инвариант RatPoly.
        Функция абстракции: см. функцию абстракции RatPoly.
        @requires: degree - целое число.
        @modifies: None
        @effects: Ищет коэффициент при x^degree.
        @throws: None
        @returns: Объект RatNum. Если степень больше реальной или отрицательная — возвращает RatNum(0). Для NaN-полинома возвращает RatNum.NaN.
        """
        if self._is_nan:
            return RatNum.NaN
        if degree < 0 or degree >= len(self._coeffs):
            return RatNum(0)
        return self._coeffs[degree]

    def is_nan(self) -> bool:
        """
        Краткое описание: Проверка полинома на NaN.
        Поля представления: _coeffs, _is_nan
        Инвариант представления: см. канонический инвариант RatPoly.
        Функция абстракции: см. функцию абстракции RatPoly.
        @requires: None
        @modifies: None
        @effects: Проверяет состояние флага NaN.
        @throws: None
        @returns: True, если полином является NaN, иначе False.
        """
        return self._is_nan

    def scale_coeff(self, rat_num: RatNum) -> 'RatPoly':
        """
        Краткое описание: Умножение полинома на скаляр (число).
        Поля представления: _coeffs, _is_nan
        Инвариант представления: см. канонический инвариант RatPoly.
        Функция абстракции: см. функцию абстракции RatPoly.
        @requires: rat_num != None и является экземпляром RatNum.
        @modifies: None
        @effects: Умножает каждый коэффициент полинома на число rat_num.
        @throws: TypeError если rat_num не является экземпляром RatNum.
        @returns: Новый объект RatPoly. Если один из элементов NaN, результат — NaN-полином.
        """
        if not isinstance(rat_num, RatNum):
            raise TypeError("rat_num must be a RatNum instance")
        if self._is_nan or rat_num.is_nan():
            return RatPoly._create_nan()
        if rat_num == RatNum(0):
            return RatPoly([RatNum(0)])
        return RatPoly([c * rat_num for c in self._coeffs])

    def __neg__(self) -> 'RatPoly':
        """
        Краткое описание: Аддитивная инверсия полинома (унарный минус).
        Поля представления: _coeffs, _is_nan
        Инвариант представления: см. канонический инвариант RatPoly.
        Функция абстракции: см. функцию абстракции RatPoly.
        @requires: None
        @modifies: None
        @effects: Меняет знак всех коэффициентов полинома на противоположный.
        @throws: None
        @returns: Новый инвертированный объект RatPoly.
        """
        if self._is_nan:
            return self
        return RatPoly([-c for c in self._coeffs])

    def __add__(self, other: 'RatPoly') -> 'RatPoly':
        """
        Краткое описание: Сложение двух полиномов.
        Поля представления: _coeffs, _is_nan
        Инвариант представления: см. канонический инвариант RatPoly.
        Функция абстракции: см. функцию абстракции RatPoly.
        @requires: other != None и является экземпляром RatPoly.
        @modifies: None
        @effects: Почленно складывает коэффициенты при одинаковых степенях x.
        @throws: None
        @returns: Новый объект RatPoly (сумма). Если один из них NaN, результат — NaN.
        """
        if self._is_nan or other._is_nan:
            return RatPoly._create_nan()
        max_len = max(len(self._coeffs), len(other._coeffs))
        new_coeffs = []
        for i in range(max_len):
            c1 = self.get_coeff(i)
            c2 = other.get_coeff(i)
            new_coeffs.append(c1 + c2)
        return RatPoly(new_coeffs)

    def __sub__(self, other: 'RatPoly') -> 'RatPoly':
        """
        Краткое описание: Вычитание полиномов.
        Поля представления: _coeffs, _is_nan
        Инвариант представления: см. канонический инвариант RatPoly.
        Функция абстракции: см. функцию абстракции RatPoly.
        @requires: other != None
        @modifies: None
        @effects: Вычитает полином other из текущего полинома.
        @throws: None
        @returns: Новый объект RatPoly (разность).
        """
        return self + (-other)

    def __mul__(self, other: 'RatPoly') -> 'RatPoly':
        """
        Краткое описание: Умножение полиномов.
        Поля представления: _coeffs, _is_nan
        Инвариант представления: см. канонический инвариант RatPoly.
        Функция абстракции: см. функцию абстракции RatPoly.
        @requires: other != None
        @modifies: None
        @effects: Вычисляет произведение двух полиномов по правилу раскрытия скобок.
        @throws: None
        @returns: Новый объект RatPoly (произведение).
        """
        if self._is_nan or other._is_nan:
            return RatPoly._create_nan()
        if self == RatPoly([RatNum(0)]) or other == RatPoly([RatNum(0)]):
            return RatPoly([RatNum(0)])
        len_res = len(self._coeffs) + len(other._coeffs) - 1
        res_coeffs = [RatNum(0)] * len_res
        for i, c1 in enumerate(self._coeffs):
            for j, c2 in enumerate(other._coeffs):
                res_coeffs[i + j] = res_coeffs[i + j] + (c1 * c2)
        return RatPoly(res_coeffs)

    def __truediv__(self, other: 'RatPoly') -> 'RatPoly':
        """
        Краткое описание: Деление полиномов столбиком (нахождение целой части).
        Поля представления: _coeffs, _is_nan
        Инвариант представления: см. канонический инвариант RatPoly.
        Функция абстракции: см. функцию абстракции RatPoly.
        @requires: other != None и не равен нулевому полиному.
        @modifies: None
        @effects: Находит частное от деления self на other методом деления уголком многочленов.
        @throws: None
        @returns: Новый объект RatPoly (частное). При делении на 0 или NaN возвращает NaN-полином.
        """
        if self._is_nan or other._is_nan or other == RatPoly([RatNum(0)]):
            return RatPoly._create_nan()
        remainder = list(self._coeffs)
        quotient_coeffs = [RatNum(0)] * max(1, len(self._coeffs) - len(other._coeffs) + 1)
        while len(remainder) >= len(other._coeffs) and not (len(remainder) == 1 and remainder[0] == RatNum(0)):
            deg_rem = len(remainder) - 1
            deg_div = len(other._coeffs) - 1
            deg_q = deg_rem - deg_div
            lead_rem = remainder[-1]
            lead_div = other._coeffs[-1]
            q_coeff = lead_rem / lead_div
            quotient_coeffs[deg_q] = q_coeff
            for i, c in enumerate(other._coeffs):
                remainder[deg_q + i] = remainder[deg_q + i] - (c * q_coeff)
            while len(remainder) > 1 and remainder[-1] == RatNum(0):
                remainder.pop()
        return RatPoly(quotient_coeffs)

    def eval(self, rat_num: RatNum) -> RatNum:
        """
        Краткое описание: Вычисление значения полинома в точке.
        Поля представления: _coeffs, _is_nan
        Инвариант представления: см. канонический инвариант RatPoly.
        Функция абстракции: см. функцию абстракции RatPoly.
        @requires: rat_num != None
        @modifies: None
        @effects: Вычисляет P(rat_num) с использованием эффективной схемы Горнера.
        @throws: None
        @returns: Значение в точке в виде объекта RatNum. Если полином или точка NaN, возвращает RatNum.NaN.
        """
        if self._is_nan or rat_num.is_nan():
            return RatNum.NaN
        res = RatNum(0)
        for c in reversed(self._coeffs):
            res = res * rat_num + c
        return res

    def differentiate(self) -> 'RatPoly':
        """
        Краткое описание: Взятие производной полинома.
        Поля представления: _coeffs, _is_nan
        Инвариант представления: см. канонический инвариант RatPoly.
        Функция абстракции: см. функцию абстракции RatPoly.
        @requires: None
        @modifies: None
        @effects: Вычисляет первую производную многочлена.
        @throws: None
        @returns: Новый объект RatPoly (производная).
        """
        if self._is_nan:
            return self
        if len(self._coeffs) <= 1:
            return RatPoly([RatNum(0)])
        new_coeffs = [self._coeffs[i] * RatNum(i) for i in range(1, len(self._coeffs))]
        return RatPoly(new_coeffs)

    def anti_differentiate(self, integration_constant: RatNum) -> 'RatPoly':
        """
        Краткое описание: Нахождение неопределённого интеграла полинома.
        Поля представления: _coeffs, _is_nan
        Инвариант представления: см. канонический инвариант RatPoly.
        Функция абстракции: см. функцию абстракции RatPoly.
        @requires: integration_constant != None
        @modifies: None
        @effects: Находит неопределенный интеграл с заданной константой интегрирования.
        @throws: None
        @returns: Новый объект RatPoly (первообразная). Если константа NaN, возвращает NaN-полином.
        """
        if self._is_nan or integration_constant.is_nan():
            return RatPoly._create_nan()
        new_coeffs = [integration_constant]
        for i, c in enumerate(self._coeffs):
            new_coeffs.append(c / RatNum(i + 1))
        return RatPoly(new_coeffs)

    def integrate(self, lower_bound: RatNum, upper_bound: RatNum) -> RatNum:
        """
        Краткое описание: Вычисление определенного интеграла.
        Поля представления: _coeffs, _is_nan
        Инвариант представления: см. канонический инвариант RatPoly.
        Функция абстракции: см. функцию абстракции RatPoly.
        @requires: lower_bound != None, upper_bound != None
        @modifies: None
        @effects: Вычисляет определенный интеграл на отрезке с помощью формулы Ньютона-Лейбница.
        @throws: None
        @returns: Значение интеграла (RatNum).
        """
        if self._is_nan or lower_bound.is_nan() or upper_bound.is_nan():
            return RatNum.NaN
        antidiff = self.anti_differentiate(RatNum(0))
        return antidiff.eval(upper_bound) - antidiff.eval(lower_bound)

    @staticmethod
    def value_of(string: str) -> 'RatPoly':
        """
        Краткое описание: Фабричный метод генерации из строки.
        Поля представления: Нет (статичный метод)
        Инвариант представления: Зависит от создаваемого инварианта класса.
        Функция абстракции: Парсит строковую абстракцию в объект структуры данных.
        @requires: string — валидная строка.
        @modifies: None
        @effects: Десериализует строку в полином.
        @throws: ValueError / NotImplementedError при сложных паттернах строки.
        @returns: Объект RatPoly.
        """
        if string.strip() == "NaN":
            return RatPoly._create_nan()
        if 'x' not in string:
            try:
                parts = string.split('/')
                if len(parts) == 2:
                    return RatPoly([RatNum(int(parts[0]), int(parts[1]))])
                return RatPoly([RatNum(int(string))])
            except ValueError:
                return RatPoly._create_nan()
        raise NotImplementedError("Сложный парсер строк не реализован. Используйте прямую инициализацию через массив коэффициентов.")

    def __str__(self) -> str:
        """
        Краткое описание: Строковое представление полинома.
        Поля представления: _coeffs, _is_nan
        Инвариант представления: см. канонический инвариант RatPoly.
        Функция абстракции: см. функцию абстракции RatPoly.
        @requires: None
        @modifies: None
        @effects: Формирует читаемую строку уравнения (например, "3*x^2 + 2*x + 1").
        @throws: None
        @returns: Строка (str).
        """
        if self._is_nan:
            return "NaN"
        if len(self._coeffs) == 1 and self._coeffs[0] == RatNum(0):
            return "0"
        parts = []
        for i, c in enumerate(self._coeffs):
            if c == RatNum(0):
                continue
            c_str = str(c)
            if i == 0:
                parts.append(c_str)
            elif i == 1:
                parts.append(f"{c_str}*x" if c_str != "1" else "x")
            else:
                parts.append(f"{c_str}*x^{i}" if c_str != "1" else f"x^{i}")
        return " + ".join(reversed(parts))

    def __hash__(self) -> int:
        """
        Краткое описание: Хэширование полинома.
        Поля представления: _coeffs, _is_nan
        Инвариант представления: см. канонический инвариант RatPoly.
        Функция абстракции: см. функцию абстракции RatPoly.
        @requires: None
        @modifies: None
        @effects: Вычитляет хэш-код на основе кортежа коэффициентов.
        @throws: None
        @returns: Целое число (int).
        """
        if self._is_nan:
            return hash("NaN")
        return hash(tuple(self._coeffs))

    def __eq__(self, other) -> bool:
        """
        Краткое описание: Сравнение полиномов на равенство.
        Поля представления: _coeffs, _is_nan
        Инвариант представления: см. канонический инвариант RatPoly.
        Функция абстракции: см. функцию абстракции RatPoly.
        @requires: None
        @modifies: None
        @effects: Проверяет совпадение всех коэффициентов двух полиномов.
        @throws: None
        @returns: True, если полиномы эквивалентны, иначе False.
        """
        if not isinstance(other, RatPoly):
            return False
        if self._is_nan and other._is_nan:
            return True
        if self._is_nan or other._is_nan:
            return False
        return self._coeffs == other._coeffs

RatPoly.NaN = RatPoly(is_nan=True)


class TestRatSolution(unittest.TestCase):
    
    # ==========================================
    # ТЕСТЫ ДЛЯ RatNum (Рациональные числа)
    # ==========================================

    def test_1_rat_num_init_and_canonical(self):
        r1 = RatNum(2, 4)
        self.assertEqual(r1._num, 1)
        self.assertEqual(r1._den, 2)
        r2 = RatNum(3, -6)
        self.assertEqual(r2._num, -1)
        self.assertEqual(r2._den, 2)
        with self.assertRaises(TypeError):
            RatNum("1", 2)

    def test_2_rat_num_nan_handling(self):
        nan = RatNum(1, 0)
        self.assertTrue(nan.is_nan())
        self.assertEqual(str(nan), "NaN")
        self.assertTrue((nan + RatNum(1)).is_nan())

    def test_3_rat_num_signs(self):
        neg = RatNum(-5, 2)
        pos = RatNum(5, 2)
        zero = RatNum(0, 1)
        nan = RatNum(1, 0)
        
        self.assertTrue(neg.is_negative())
        self.assertFalse(neg.is_positive())
        self.assertTrue(pos.is_positive())
        self.assertFalse(zero.is_negative())
        self.assertFalse(nan.is_positive())

    def test_4_rat_num_compare_to(self):
        a = RatNum(1, 3)
        b = RatNum(1, 2)
        nan = RatNum(1, 0)
        
        self.assertEqual(a.compare_to(b), -1)
        self.assertEqual(b.compare_to(a), 1)
        self.assertEqual(a.compare_to(a), 0)
        self.assertEqual(nan.compare_to(b), 1)
        self.assertEqual(nan.compare_to(nan), 0)
        with self.assertRaises(TypeError):
            a.compare_to("not a RatNum")

    def test_5_rat_num_conversions(self):
        r = RatNum(5, 2)
        nan = RatNum(1, 0)
        
        self.assertAlmostEqual(r.float_value(), 2.5)
        self.assertEqual(r.int_value(), 2)
        
        with self.assertRaises(ValueError):
            nan.float_value()
        with self.assertRaises(ValueError):
            nan.int_value()

    def test_6_rat_num_unary_neg(self):
        r = RatNum(3, 4)
        self.assertEqual(str(-r), "-3/4")
        self.assertEqual(str(-(-r)), "3/4")
        nan = RatNum(1, 0)
        self.assertTrue((-nan).is_nan())

    def test_7_rat_num_arithmetic(self):
        a = RatNum(1, 2)
        b = RatNum(1, 3)
        zero = RatNum(0)
        
        self.assertEqual(a + b, RatNum(5, 6))
        self.assertEqual(a - b, RatNum(1, 6))
        self.assertEqual(a * b, RatNum(1, 6))
        self.assertEqual(a / b, RatNum(3, 2))
        self.assertTrue((a / zero).is_nan())

    def test_8_rat_num_hash_and_eq(self):
        r1 = RatNum(1, 2)
        r2 = RatNum(2, 4)
        r3 = RatNum(1, 3)
        
        self.assertEqual(r1, r2)
        self.assertNotEqual(r1, r3)
        self.assertEqual(hash(r1), hash(r2))
        self.assertFalse(r1 == "строка")

    # ==========================================
    # ТЕСТЫ ДЛЯ RatPoly (Полиномы)
    # ==========================================

    def test_9_rat_poly_init_and_degree(self):
        p = RatPoly([RatNum(1), RatNum(2), RatNum(0), RatNum(0)])
        self.assertEqual(p.degree(), 1)
        
        zero_poly = RatPoly([])
        self.assertEqual(zero_poly.degree(), 0)

    def test_10_rat_poly_get_coeff(self):
        p = RatPoly([RatNum(5), RatNum(0), RatNum(3)])
        self.assertEqual(p.get_coeff(0), RatNum(5))
        self.assertEqual(p.get_coeff(1), RatNum(0))
        self.assertEqual(p.get_coeff(2), RatNum(3))
        self.assertEqual(p.get_coeff(100), RatNum(0))

    def test_11_rat_poly_nan_propagation(self):
        p_clean = RatPoly([RatNum(1), RatNum(2)])
        p_nan = RatPoly([RatNum(1), RatNum(1, 0), RatNum(3)])
        
        self.assertFalse(p_clean.is_nan())
        self.assertTrue(p_nan.is_nan())
        self.assertEqual(str(p_nan), "NaN")

    def test_12_rat_poly_scale_coeff(self):
        p = RatPoly([RatNum(1), RatNum(2)])
        scaled = p.scale_coeff(RatNum(3))
        self.assertEqual(scaled.get_coeff(1), RatNum(6))
        self.assertEqual(scaled.get_coeff(0), RatNum(3))
        
        with self.assertRaises(TypeError):
            p.scale_coeff(5)

    def test_13_rat_poly_add_sub_neg(self):
        p1 = RatPoly([RatNum(1), RatNum(2)])
        p2 = RatPoly([RatNum(3), RatNum(4)])
        
        self.assertEqual(p1 + p2, RatPoly([RatNum(4), RatNum(6)]))
        self.assertEqual(p2 - p1, RatPoly([RatNum(2), RatNum(2)]))
        self.assertEqual(-p1, RatPoly([RatNum(-1), RatNum(-2)]))

    def test_14_rat_poly_mul_div(self):
        divisor = RatPoly([RatNum(-1), RatNum(1)])
        expected_quotient = RatPoly([RatNum(1), RatNum(1), RatNum(1)])
        dividend = RatPoly([RatNum(-1), RatNum(0), RatNum(0), RatNum(1)])
        
        self.assertEqual(divisor * expected_quotient, dividend)
        self.assertEqual(dividend / divisor, expected_quotient)

    def test_15_rat_poly_calculus(self):
        p = RatPoly([RatNum(0), RatNum(0), RatNum(3)])
        self.assertEqual(p.eval(RatNum(2)), RatNum(12))
        self.assertEqual(str(p.differentiate()), "6*x")
        anti = p.anti_differentiate(RatNum(5))
        self.assertEqual(anti.get_coeff(0), RatNum(5))
        self.assertEqual(anti.get_coeff(3), RatNum(1))
        self.assertEqual(p.integrate(RatNum(0), RatNum(2)), RatNum(8))

    def test_16_rat_poly_strings_hash_eq(self):
        p1 = RatPoly([RatNum(1), RatNum(0), RatNum(2)])
        p2 = RatPoly([RatNum(1), RatNum(0), RatNum(2)])
        
        self.assertEqual(str(p1), "2*x^2 + 1")
        self.assertEqual(p1, p2)
        self.assertEqual(hash(p1), hash(p2))
        
        parsed = RatPoly.value_of("5/2")
        self.assertEqual(parsed.get_coeff(0), RatNum(5, 2))

if __name__ == '__main__':
    unittest.main()
