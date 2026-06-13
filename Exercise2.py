import math

# Объявляем функцию с преобразованиями и расчётами

def find_time(d1, d2, h, v_sand, n, theta1):

    # Переводим ярды в футы, миль/час в  фут/секунда
    d1_foot = d1 * 3       
    h_foot = h * 3         
    v_sand_footpsec = v_sand * 5280 / 3600

    # Рассчёты согласно задаче
    x = d1_foot * math.tan(math.radians(theta1))
    L1 = math.sqrt(x**2 + d1_foot**2)
    L2 = math.sqrt((h_foot - x)**2 + d2**2)
    t = (1 / v_sand_footpsec) * (L1 + n * L2)
    return round(t, 1)


# Взаимодействие с пользователем
def get_user_inputs():
    d1 = input('Введите кратчайшее расстояние между спасателем и кромкой воды, d1 (ярды) => ')
    print(d1)
    d1 = float(d1)

    d2 = input('Введите кратчайшее расстояние от утопающего до берега, d2 (футы) => ')
    print(d2)
    d2 = float(d2)

    h = input('Введите боковое смещение между спасателем и утопающим, h (ярды) => ')
    print(h)
    h = float(h)

    v_sand = input('Введите скорость движения спасателя по песку, v_sand (мили в час) => ')
    print(v_sand)
    v_sand = float(v_sand)

    n = input('Введите коэффициент замедления спасателя при движении в воде, n => ')
    print(n)
    n = float(n)

    theta1 = input('Введите направление движения спасателя по песку, theta1 (градусы) => ')
    print(theta1)
    theta1 = float(theta1)
    
    return d1, d2, h, v_sand, n, theta1

# Функция вывода результата на экран
def print_result(theta1, t_rounded):
    angle_int = int(theta1)
    print('Если спасатель начнёт движение под углом theta1, равным', angle_int, 'градусам, он')
    print('достигнет утопающего через', t_rounded, 'секунды')


def main(): 
    # 1. Получаем данные от пользователя
    d1, d2, h, v_sand, n, theta1 = get_user_inputs()
    if abs(theta1) >= 90:
        print('Ошибка: Угол должен быть строго меньше 90 градусов, иначе спасатель пойдет параллельно берегу!')
        return
    # 2. Считаем
    result_time = find_time(d1, d2, h, v_sand, n, theta1)
    
    # 3. Выводим результат
    print_result(theta1, result_time)


# Тесты
print('Запуск модульных тестов')

# Тест 1: Спасатель  с условиями test1_expected_output из примера задания 1
test_t1 = find_time(d1=8, d2=10, h=50, v_sand=5, n=2, theta1=39.413)
assert test_t1 == 39.9, f'Тест 1 провален! Ожидалось 39.9, но получено {test_t1}'

# Тест 2: Спасатель с условиями test2_expected_output из примера задания 1
test_t2 = find_time(d1=40, d2=100, h=42, v_sand=12, n=2, theta1=30)
assert test_t2 == 20.9, f'Тест 2 провален! Ожидалось 20.9, но получено {test_t2}'

# Тест 3: Спасатель c данными от нейросети №1
test_t3 = find_time(d1=10, d2=30, h=0, v_sand=5, n=1.5, theta1=0)
assert test_t3 == 10.2, f'Тест 3 провален! Ожидалось 10.2, но получено {test_t3}'

# Тест 4: Спасатель c данными от нейросети №2
test_t4 = find_time(d1=10, d2=30, h=10, v_sand=5, n=1.5, theta1=30)
assert test_t4 == 11.4, f'Тест 4 провален! Ожидалось 11.4, но получено {test_t4}'

# Тест 5: Спасатель c данными от test3_expected_output из примера задания 1
test_t5 = find_time(d1=14, d2=23, h=70, v_sand=6, n=2, theta1=25)
assert test_t5 == 48.9, f'Тест 5 провален! Ожидалось 48.9, но получено {test_t5}'

# Тест 6: Спасатель  с условиями test4_expected_output из примера задания 1
test_t6 = find_time(d1=53, d2=15, h=800, v_sand=11, n=3, theta1=47)
assert test_t6 == 429, f'Тест 6 провален! Ожидалось 429, но получено {test_t6}'

# Тест 7: Спасатель  с условиями test5_expected_output из примера задания 1
test_t7 = find_time(d1=30, d2=45, h=100, v_sand=6, n=1, theta1=7)
assert test_t7 == 43.5, f'Тест 7 провален! Ожидалось 43.5, но получено {test_t7}'

# Тест 8: Спасатель  с условиями test6_expected_output из примера задания 1
test_t8 = find_time(d1=33, d2=20, h=48, v_sand=9, n=3, theta1=32)
assert test_t8 == 28.1, f'Тест 8 провален! Ожидалось 28.1, но получено {test_t8}'

# Тест 9: Спасатель  с условиями test7_expected_output из примера задания 1
test_t9 = find_time(d1=7, d2=9, h=47, v_sand=4, n=3, theta1=5)
assert test_t9 == 74.9, f'Тест 9 провален! Ожидалось 74.9, но получено {test_t9}'

# Тест 10: Спасатель  с условиями test8_expected_output из примера задания 1
test_t10 = find_time(d1=80, d2=20, h=120, v_sand=10, n=2, theta1=25)
assert test_t10 == 52.0, f'Тест 10 провален! Ожидалось 52.0, но получено {test_t10}'

print('Тесты успешно пройдены')

# Условие для запуска основной программы
if __name__ == '__main__':
    main()
