# РУКОВОДСТВО АДМИНИСТРАТОРА
## Техническое сопровождение и развертывание комплекса «Морской бой»

### Содержание
1. [Архитектура и состав файлов](#1-архитектура-и-состав-файлов)
2. [Развертывание и автоматизация](#2-развертывание-и-автоматизация)
3. [Листинги скриптов сборки и деплоя](#3-листинги-скриптов-сборки-и-деплоя)
4. [Спецификация конфигураций и баз данных (JSON)](#4-спецификация-конфигураций-и-баз-данных-json)
5. [Поддержка жизненного цикла и безопасность](#5-поддержка-жизненного-цикла-и-безопасность)

---

### 1. Архитектура и состав файлов
```text
battleship_project/
│
├── battleship.py       # Основной исполнительный модуль (Tkinter GUI)
├── test_battleship.py  # Модульные тесты автоматической проверки (Unittest)
├── README_USER.md      # Документ пользователя
├── README_ADMIN.md     # Данное руководство (Руководство администратора)
│
├── deploy_windows.bat  # Запуск модульных тестов и развертывание под Windows
├── deploy_linux.sh     # Скрипт развертывания под Linux
├── build_windows.bat   # Компиляция автономного .exe через PyInstaller
└── build_linux.sh      # Компиляция бинарного файла Linux
```

### 2. Развертывание и автоматизация
#### Автоматический запуск (Windows):
Запустить `deploy_windows.bat`. Скрипт переведет консоль в кодировку UTF-8, выполнит автоматическое тестирование стабильности кода через изолированный модуль `test_battleship.py` и, при успешном прохождении тестов, запустит игру через локальный интерпретатор. При сбое тестов запуск блокируется.

#### Автоматический запуск (Linux):
Выполнить `./deploy_linux.sh`. Скрипт проверит дистрибутив (поддерживаются Debian/Ubuntu и RedHat/Fedora) и автоматически доставит системный пакет `python3-tk` / `python3-tkinter` в случае его отсутствия, запустит тесты и откроет игру.

#### Финальная компиляция (Сборка в бинарные файлы):
Для исключения необходимости установки интерпретатора Python на целевых машинах предусмотрены скрипты компиляции через `pyinstaller`. Сборка выполняется локально под целевую ОС (запуск `build_windows.bat` в Windows или `./build_linux.sh` в Linux). 
* **Под Windows:** Генерируется независимый файл `dist/Battleship.exe`. Флаг `--noconsole` скрывает черное окно командной строки.
* **Под Linux:** Генерируется бинарный файл `dist/Battleship`. Скрипт использует безопасный флаг `--user` для обхода ограничений внешне управляемых сред (PEP 668) без поломки системных пакетов.

---

### 3. Листинги скриптов сборки и деплоя

#### deploy_windows.bat
```batch
@echo off
chcp 65001 > nul

echo START_TESTS
python -m unittest test_battleship.py

if %errorlevel% neq 0 (
    echo TEST_FAILED
    pause
    exit /b
)

echo TEST_SUCCESS_START_GAME
python battleship.py
```

#### build_windows.bat
```batch
@echo off
:: Принудительно включаем поддержку UTF-8 в консоли Windows
chcp 65001 > nul

echo [BUILD] Installing PyInstaller...
pip install pyinstaller

echo [BUILD] Compiling to autonomous EXE...
pyinstaller --noconsole --onefile --name="Battleship" battleship.py

echo [BUILD] Done! Check the 'dist' folder.
pause
```

#### deploy_linux.sh
```bash
#!/bin/bash
echo "[СИСТЕМА] Проверка окружения Linux..."

if [ -f /etc/debian_version ]; then
    if ! dpkg -s python3-tk >/dev/null 2>&1; then
        echo "[СИСТЕМА] Установка зависимостей..."
        sudo apt-get update -y && sudo apt-get install python3-tk python3 -y
    fi
elif [ -f /etc/redhat-release ]; then
    if ! rpm -q python3-tkinter >/dev/null 2>&1; then
        echo "[СИСТЕМА] Установка зависимостей..."
        sudo dnf install python3-tkinter -y
    fi
fi

echo "[СИСТЕМА] Запуск тестов..."
python3 -m unittest test_battleship.py

if [ \$? -eq 0 ]; then
    echo "[СИСТЕМА] Запуск игры..."
    python3 battleship.py
else
    echo "[ОШИБКА] Тесты провалились! Запуск отменён."
    exit 1
fi
```

#### build_linux.sh
```bash
#!/bin/bash
echo "[СБОРКА] Компиляция под Linux..."

pip3 install --user pyinstaller

echo "[СБОРКА] Запуск PyInstaller..."
~/.local/bin/pyinstaller --onefile --name="Battleship" battleship.py

if [ \$? -eq 0 ]; then
    echo "[СБОРКА] Готово в dist/Battleship"
else
    echo "[ОШИБКА] Сборка провалилась!"
    exit 1
fi
```

---

### 4. Спецификация конфигураций и баз данных (JSON)

#### Файл настроек: config.json

| Параметр | Тип | Назначение |
| :--- | :--- | :--- |
| `window_size` | string | Геометрия окна (например, "900x650") |
| `bg_color` | string | Hex-код фона интерфейса (например, "#2c3e50") |
| `grid_color` | string | Hex-код цвета игрового поля (например, "#34495e") |
| `font_family` | string | Шрифт элементов интерфейса |
| `font_size` | integer | Базовый размер шрифта |
| `game_mode` | string | Режим игры ("vs Computer" / "Hotseat") |
| `difficulty` | string | Уровень сложности искусственного интеллекта ("Easy" / "Normal") |

#### Файл локальной БД рекордов: highscores.json
Файл представляет собой массив JSON (`list[dict]`), содержащий профили участников.
```json
[
    {"name": "Игрок 1", "wins": 0},
    {"name": "Игрок 2", "wins": 0},
    {"name": "Computer", "wins": 0}
]
```
При добавлении нового игрока в режиме Hotseat, система динамически дописывает новый объект со структурой `{"name": "<Имя>", "wins": 1}`.

---

### 5. Поддержка жизненного цикла и безопасность
* **Отказоустойчивость данных:** Чтение файлов конфигурации обернуто в блоки `try-except`. В случае повреждения структуры JSON файлов `config.json` или `highscores.json` (например, некорректное ручное редактирование администратором), игра не завершается аварийно, а автоматически перезаписывает поврежденный файл эталонными дефолтными значениями из кода.
* **Резервное копирование:** В рамках обеспечения сохранности данных пользователей, администратору рекомендуется настроить регулярное резервное копирование файла рекордов `highscores.json` по графику (например, раз в неделю).
