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
python3 -m unittest test_battleship

if [ $? -eq 0 ]; then
    echo "[СИСТЕМА] Запуск игры..."
    python3 battleship.py
else
    echo "[ОШИБКА] Тесты провалились! Запуск отменён."
    exit 1
fi
