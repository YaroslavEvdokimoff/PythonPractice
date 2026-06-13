import math

def find_time(d1, d2, h, v_sand, n, theta1):
    # Перевод данных к единому формату (в футы, футы в секунду)
    d1_foot = d1 * 3                              
    h_foot = h * 3         
    v_sand_footpsec = v_sand * 5280 / 3600

    # Ограничиваем угол, чтобы избежать деления на ноль при tan(90)
    if abs(theta1) >= 90:                         
        return float('inf')

    # Расчёт времени для конкретного угла theta1
    x = d1_foot * math.tan(math.radians(theta1))  
    L1 = math.sqrt(x**2 + d1_foot**2)
    L2 = math.sqrt((h_foot - x)**2 + d2**2)
    t = (1 / v_sand_footpsec) * (L1 + n * L2)
    return t


def find_optimal_angle(d1, d2, h, v_sand, n):     
    # Функция подбора оптимального угла
    best_theta = 0
    min_time = float('inf')
    
    # Ищем по всему физически возможному диапазону углов от 0 до 89.9 градусов.
    # Шаг 0.01 градуса.
    start_index = 0
    end_index = 8991
    
    for i in range(start_index, end_index):                  
        theta1 = i * 0.01
        current_time = find_time(d1, d2, h, v_sand, n, theta1)
        
        if current_time < min_time:
            min_time = current_time
            best_theta = theta1
            
    return round(best_theta, 2), round(min_time, 1)

def get_user_inputs():
    d1 = float(input('Введите кратчайшее расстояние между спасателем и кромкой воды, d1 (ярды) => '))
    print(d1)
    d2 = float(input('Введите кратчайшее расстояние от утопающего до берега, d2 (футы) => '))
    print(d2)
    h = float(input('Введите боковое смещение между спасателем и утопающим, h (ярды) => '))
    print(h)
    v_sand = float(input('Введите скорость движения спасателя по песку, v_sand (мили в час) => '))
    print(v_sand)
    n = float(input('Введите коэффициент замедления спасателя при движении в воде, n => '))
    print(n)
    return d1, d2, h, v_sand, n

def run_tests():
    print('Запуск тестов')
    
    # Тест 1: Параметры из примера 1 (настоящий оптимальный угол 80.56°)
    angle, _ = find_optimal_angle(d1=8, d2=10, h=50, v_sand=5, n=2)
    assert angle == 80.56, f'Тест 1 провален! Ожидалось 80.56, получен угол {angle}'
    
    # Тест 2: Параметры из примера 2
    angle, _ = find_optimal_angle(d1=40, d2=100, h=42, v_sand=12, n=2)
    assert angle == 37.97, f'Тест 2 провален! Ожидалось 37.97, получен угол {angle}'
    
    # Тест 3: Параметры из примера 5
    angle, _ = find_optimal_angle(d1=14, d2=23, h=70, v_sand=6, n=2)
    assert angle == 77.97, f'Тест 3 провален! Ожидалось 77.97, получен угол {angle}'
    
    # Тест 4: Параметры из примера 6 (экстремальное h=800)
    angle, _ = find_optimal_angle(d1=53, d2=15, h=800, v_sand=11, n=3)
    assert angle == 86.20, f'Тест 4 провален! Ожидалось 86.20, получен угол {angle}'
    
    # Тест 5: Параметры из примера 7 (минимальное n=1)
    angle, _ = find_optimal_angle(d1=30, d2=45, h=100, v_sand=6, n=1)
    assert angle == 65.77, f'Тест 5 провален! Ожидалось 65.77, получен угол {angle}'
    
    # Тест 6: Параметры из примера 8
    angle, _ = find_optimal_angle(d1=33, d2=20, h=48, v_sand=9, n=3)
    assert angle == 54.42, f'Тест 6 провален! Ожидалось 54.42, получен угол {angle}'
    
    # Тест 7: Параметры из примера 9
    angle, _ = find_optimal_angle(d1=7, d2=9, h=47, v_sand=4, n=3)
    assert angle == 81.34, f'Тест 7 провален! Ожидалось 81.34, получен угол {angle}'
    
    # Тест 8: Параметры из примера 10
    angle, _ = find_optimal_angle(d1=80, d2=20, h=120, v_sand=10, n=2)
    assert angle == 55.63, f'Тест 8 провален! Ожидалось 55.63, получен угол {angle}'
    
    # Тест 9: Спасатель и утопающий на одной линии (h=0), угол равен 0 градусов
    angle, _ = find_optimal_angle(d1=10, d2=30, h=0, v_sand=5, n=1.5)
    assert angle == 0, f'Тест 9 провален! Ожидалось 0, получен угол {angle}'
    
    # Тест 10: Спасатель уже на кромке воды (d1=0), угол равен 0 градусов
    angle, _ = find_optimal_angle(d1=0, d2=20, h=10, v_sand=5, n=2)
    assert angle == 0, f'Тест 10 провален! Ожидалось 0, получен угол {angle}'
    
    print('Все 10 тестов успешно пройдены!')

def main(): 
    # Сначала проверяем алгоритм тестами
    run_tests()
    
    print('Ввод параметров задачи')
    d1, d2, h, v_sand, n = get_user_inputs()
    
    # Получаем лучший угол и минимальное время через численный перебор
    opt_theta, min_time = find_optimal_angle(d1, d2, h, v_sand, n) 
    
    print('Результат')
    print(f'Оптимальный угол движения по песку (theta1): {opt_theta}°')
    print(f'Минимальное время за которое спасатель доберётся до утопающего: {min_time} сек.')

if __name__ == '__main__':
    main()
