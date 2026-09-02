# Задание 9: Итераторы и генераторы
import unittest
import types

class Fibo:
    """
    Класс итераторов, который перечисляет все числа Фибоначчи.
    Последовательность начинается с 0, 1, 1, 2, 3, ...
    Использует только операцию сложения.
    """
    def __init__(self):
        self.current = 0
        self.next_val = 1
        self.is_first = True

    def __iter__(self):
        return self

    def __next__(self):
        if self.is_first:
            self.is_first = False
            return self.current
        
        result = self.next_val
        self.next_val = self.current + self.next_val
        self.current = result
        return result


def integers():
    """
    Генератор, который перечисляет все неотрицательные целые числа
    по возрастанию начиная с 0.
    """
    num = 0
    while True:
        yield num
        num += 1


def primes():
    """
    Оптимизированный генератор простых чисел.
    Проверяет делимость только на уже найденные простые числа.
    """
    found_primes = []
    num = 2
    while True:
        is_prime = True
        for p in found_primes:
            if p * p > num:
                break
            if num % p == 0:
                is_prime = False
                break
        
        if is_prime:
            found_primes.append(num)
            yield num
        num += 1


class TestIteratorsAndGenerators(unittest.TestCase):

    # --- ТЕСТЫ ДЛЯ FIBO ---

    def test_fibo_first_elements(self):
        """1. Проверка первых 6 чисел Фибоначчи (старт с 0, 1, 1...)"""
        fibo = Fibo()
        result = [next(fibo) for _ in range(6)]
        self.assertEqual(result, [0, 1, 1, 2, 3, 5])

    def test_fibo_independent_instances(self):
        """2. Проверка независимости разных экземпляров итератора Fibo"""
        fibo1 = Fibo()
        fibo2 = Fibo()
        next(fibo1) # 0
        next(fibo1) # 1
        self.assertEqual(next(fibo1), 1)
        self.assertEqual(next(fibo2), 0)

    def test_fibo_is_iterator(self):
        """3. Проверка, что Fibo возвращает сам себя при вызове __iter__"""
        fibo = Fibo()
        self.assertIs(iter(fibo), fibo)


    # --- ТЕСТЫ ДЛЯ INTEGERS ---

    def test_integers_start_from_zero(self):
        """4. Проверка, что генератор integers действительно начинает с 0"""
        gen = integers()
        self.assertEqual(next(gen), 0)

    def test_integers_sequence(self):
        """5. Проверка строгой последовательности из 10 чисел"""
        gen = integers()
        result = [next(gen) for _ in range(10)]
        self.assertEqual(result, list(range(10)))

    def test_integers_is_generator(self):
        """6. Проверка типа возвращаемого объекта (должен быть генератором)"""
        gen = integers()
        self.assertIsInstance(gen, types.GeneratorType)


    # --- ТЕСТЫ ДЛЯ PRIMES ---

    def test_primes_first_elements(self):
        """7. Проверка первых 5 простых чисел (начиная с 2)"""
        gen = primes()
        result = [next(gen) for _ in range(5)]
        self.assertEqual(result, [2, 3, 5, 7, 11])

    def test_primes_excluding_composites(self):
        """8. Проверка, что генератор пропускает составные числа"""
        gen = primes()
        result = [next(gen) for _ in range(10)]
        self.assertNotIn(4, result)
        self.assertNotIn(9, result)
        self.assertNotIn(15, result)

    def test_prime_large_number(self):
        """9. Проверка конкретного более дальнего простого числа"""
        gen = primes()
        result = [next(gen) for _ in range(11)]
        self.assertEqual(result[-1], 31)


    # --- ОБЩИЙ ТЕСТ НА БЕСКОНЕЧНОСТЬ ---

    def test_generators_are_infinite(self):
        """10. Проверка, что вызов next() после 100 итераций не вызывает StopIteration"""
        fibo = Fibo()
        ints = integers()
        prms = primes()
        
        try:
            for _ in range(100):
                next(fibo)
                next(ints)
                next(prms)
        except StopIteration:
            self.fail("Один из итераторов/генераторов завершился ошибкой StopIteration!")


if __name__ == "__main__":
    unittest.main()
