import os
from PIL import Image, ImageDraw


def read_input_file(filename):
    with open(filename, 'r') as file:
        # Читаем первую строку и убираем пробелы
        first_line = file.readline().strip()

        # Разделяем '5x10' по символу 'x'
        dimensions = first_line.split('x')
        rows = int(dimensions[0])  # Индекс 0 — это 5
        cols = int(dimensions[1])  # Индекс 1 — это 10

        # Читаем матрицу из нулей и единиц
        grid = []
        for line in file:
            if line.strip():  # Пропускаем пустые строки
                row = [int(item) for item in line.split()]
                grid.append(row)

    return rows, cols, grid


def init_output_file(filename, rows, cols):
    # Этот код запускается ТОЛЬКО ОДИН РАЗ перед началом игры, чтобы создать чистый файл
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(f'{rows}x{cols}\n\n')


def write_output_step(filename, step, grid):
    # Этот код запускается НА КАЖДОМ ШАГЕ и дописывает матрицу в конец файла
    with open(filename, 'a', encoding='utf-8') as file:
        file.write(f'--- Шаг {step} ---\n')
        for row in grid:
            row_str = ' '.join([str(item) for item in row])
            file.write(row_str + '\n')
        file.write('\n')  # Пустая строка для отделения шагов


def count_neighbors(grid, x, y, rows, cols):
    count = 0
    # Проверяем все смещения от -1 до +1 по вертикали и горизонтали
    for dy in [-1, 0, 1]:
        for dx in [-1, 0, 1]:
            # Если смещение 0 и 0 — это сама наша клетка, её считать не нужно
            if dx == 0 and dy == 0:
                continue

            # Вычисляем координаты соседа
            neighbor_x = x + dx
            neighbor_y = y + dy

            # Проверяем, не вышли ли мы за границы игрового поля
            if 0 <= neighbor_x < cols and 0 <= neighbor_y < rows:
                # Если клетка жива (её возраст больше 0), увеличиваем счетчик
                if grid[neighbor_y][neighbor_x] > 0:
                    count += 1

    return count


def update_grid(grid, rows, cols):
    # Создаем новое пустое поле, заполненное нулями
    new_grid = [[0 for _ in range(cols)] for _ in range(rows)]

    # Проходим циклом по каждой ячейке поля
    for y in range(rows):
        for x in range(cols):
            # Считаем живых соседей
            neighbors = count_neighbors(grid, x, y, rows, cols)

            # Достаем текущее значение клетки (её текущий возраст)
            current_age = grid[y][x]

            if current_age > 0:  # Если число больше 0, значит клетка ЖИВА
                # Правило выживания Конвея
                if neighbors == 2 or neighbors == 3:
                    # Клетка выживает и её возраст увеличивается на +1!
                    new_grid[y][x] = current_age + 1
                else:
                    # Клетка погибает
                    new_grid[y][x] = 0
            else:  # Если в клетке 0, значит она мертва
                # Правило рождения Конвея
                if neighbors == 3:
                    # Рождается НОВАЯ клетка с начальным возрастом 1!
                    new_grid[y][x] = 1

    return new_grid


def save_grid_to_png(step, grid, rows, cols, base_color_name):
    cell_size = 20  # Размер одной клетки в пикселях на картинке
    img_w = cols * cell_size
    img_h = rows * cell_size

    # Создаем чистое изображение с черным фоном
    img = Image.new('RGB', (img_w, img_h), 'black')
    draw = ImageDraw.Draw(img)

    for y in range(rows):
        for x in range(cols):
            age = grid[y][x]
            if age > 0:
                # Рассчитываем затухание цвета (чем старше клетка, тем она бледнее)
                # Ограничиваем минимальную яркость на уровне 50, чтобы клетка не исчезла совсем
                intensity = max(255 - (age - 1) * 30, 50)

                # Формируем 'чистый цвет' по выбору пользователя
                if base_color_name == 'red':
                    color = (intensity, 0, 0)
                elif base_color_name == 'green':
                    color = (0, intensity, 0)
                else:  # blue
                    color = (0, 0, intensity)

                # Координаты квадрата клетки на картинке
                x0 = x * cell_size
                y0 = y * cell_size
                x1 = x0 + cell_size - 1
                y1 = y0 + cell_size - 1

                # Рисуем закрашенную клетку
                draw.rectangle([x0, y0, x1, y1], fill=color, outline='gray')

    # Создаем папку для картинок, если её нет
    if not os.path.exists('snapshots'):
        os.makedirs('snapshots')

    img.save(f'snapshots/step_{step}.png')


# Блок тестов
def run_tests():
    print('Запуск автоматических тестов')

    # Чистые, компактные и читаемые тестовые матрицы
    empty_grid = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    block_grid = [[1, 1], [1, 1]]
    blinker_grid = [[0, 1, 0], [0, 1, 0], [0, 1, 0]]

    # Тест 1: Проверка подсчета соседей на пустом поле
    assert count_neighbors(empty_grid, 1, 1, 3, 3) == 0, 'Тест 1 провален: найдены ложные соседи'

    # Тест 2: Клетка в углу стабильной фигуры должна видеть ровно 3 соседа
    assert count_neighbors(block_grid, 0, 0, 2, 2) == 3, 'Тест 2 провален: неверный подсчет в углу фигуры'

    # Тест 3: Центральная клетка "Мигалки" должна иметь ровно 2 соседа
    assert count_neighbors(blinker_grid, 1, 1, 3, 3) == 2, 'Тест 3 провален: центр мигалки видит не 2 соседей'

    # Тест 4: Проверка, что учет возраста (> 0) корректно работает для соседей
    aged_grid = [[0, 5, 0], [0, 1, 0], [0, 0, 0]]
    assert count_neighbors(aged_grid, 1, 1, 3, 3) == 1, 'Тест 4 провален: алгоритм игнорирует старых соседей'

    # Тест 5: Одинокая живая клетка должна умереть от одиночества
    lone_grid = [[0, 0, 0], [0, 1, 0], [0, 0, 0]]
    updated_lone = update_grid(lone_grid, 3, 3)
    assert updated_lone[1][1] == 0, 'Тест 5 провален: одинокая клетка выжила'

    # Тест 6: Живая клетка с 2 соседями выживает и увеличивает возраст (1 + 1 = 2)
    updated_blinker = update_grid(blinker_grid, 3, 3)
    assert updated_blinker[1][1] == 2, 'Тест 6 провален: клетка не увеличила возраст'

    # Тест 7: Мертвая клетка с ровно 3 соседями должна ожить с начальным возрастом 1
    # У вертикальной мигалки клетка слева от центра (x=0, y=1) имеет ровно 3 соседа
    assert updated_blinker[1][0] == 1, 'Тест 7 провален: новая клетка не родилась с возрастом 1'

    # Тест 8: Клетка с 4 и более соседями должна умереть от перенаселения
    overpopulated_grid = [[1, 1, 1], [1, 1, 0], [0, 0, 0]]
    updated_over = update_grid(overpopulated_grid, 3, 3)
    assert updated_over[1][1] == 0, 'Тест 8 провален: клетка выжила при перенаселении'

    # Тест 9: Проверка инициализации текстового файла истории
    test_out = 'test_output.txt'
    init_output_file(test_out, 5, 10)
    assert os.path.exists(test_out), 'Тест 9 провален: файл истории не создался'

    # Тест 10: Проверка корректности первой строки записанного файла
    with open(test_out, 'r') as f:
        first_line = f.readline().strip()
    assert first_line == '5x10', f'Тест 10 провален: неверный заголовок файла ({first_line})'

    # Аккуратно удаляем тестовый файл после завершения проверок
    if os.path.exists(test_out):
        os.remove(test_out)

    print('Все 10 тестов успешно пройдены!\n' + '=' * 30 + '\n')


if __name__ == '__main__':
    # Автоматический запуск тестов перед основной программой
    run_tests()

    r, c, start_grid = read_input_file('input.txt')
    print(f'Файл прочитан! Размер поля: {r}x{c}')

    # Запрашиваем параметры с клавиатуры
    steps_to_sim = int(input('Введите количество поколений для моделирования: '))

    print('\nВыберите базовый чистый цвет для живых ячеек:')
    print('1 - Красный (Red)\n2 - Зелёный (Green)\n3 - Синий (Blue)')
    color_choice = input('Ваш выбор (1-3): ')

    base_color = 'red'
    if color_choice == '2':
        base_color = 'green'
    elif color_choice == '3':
        base_color = 'blue'

    out_file = 'output.txt'
    init_output_file(out_file, r, c)

    # Список, куда мы будем собирать кадры для GIF-анимации
    frames = []

    # Сохраняем Шаг 0 (текст и картинку)
    write_output_step(out_file, 0, start_grid)
    save_grid_to_png(0, start_grid, r, c, base_color)

    # Открываем созданный PNG и добавляем в список кадров
    frames.append(Image.open(f'snapshots/step_0.png'))

    current_grid = start_grid
    for step in range(1, steps_to_sim + 1):
        current_grid = update_grid(current_grid, r, c)

        # Пишем в текстовый файл
        write_output_step(out_file, step, current_grid)

        # Генерируем PNG-картинку
        save_grid_to_png(step, current_grid, r, c, base_color)

        # Добавляем новый кадр в список
        frames.append(Image.open(f'snapshots/step_{step}.png'))

    # Склейка в GIF
    if frames:
        frames[0].save('simulation.gif', save_all=True, append_images=frames[1:], duration=300, loop=0)
        print('Анимация успешно сохранена в файл "simulation.gif"!')

    print(f'\nСимуляция успешно завершена!')
    print(f'Текстовая история: {out_file}')
    print(f'Снимки поля сохранены в папку "snapshots/"')
