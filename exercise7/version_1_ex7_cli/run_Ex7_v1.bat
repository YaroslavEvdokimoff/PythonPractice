@echo off
chcp 65001 > nul
title Запуск Версии 1: Консольный REPL

:: Автоматическая активация окружения, если оно развернуто в корне проекта
if exist .venv (
    call .venv\Scripts\activate.bat
)

:: Проверяем: если main.py лежит прямо в текущей папке с батником
if exist main.py (
    python main.py
    pause
    exit /b
)

:: Если main.py лежит внутри подпапки version_1_ex7_cli, заходим и запускаем
if exist version_1_ex7_cli\main.py (
    cd version_1_ex7_cli
    python main.py
    cd ..
    pause
    exit /b
)

echo [Ошибка]: Файл main.py не найден ни в текущей папке, ни в version_1_ex7_cli!
pause
