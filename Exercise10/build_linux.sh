#!/bin/bash
echo "[СБОРКА] Компиляция под Linux..."

pip3 install --user pyinstaller

echo "[СБОРКА] Запуск PyInstaller..."
~/.local/bin/pyinstaller --onefile --name="Battleship" battleship.py

if [ $? -eq 0 ]; then
    echo "[СБОРКА] Готово в dist/Battleship"
else
    echo "[ОШИБКА] Сборка провалилась!"
    exit 1
fi
