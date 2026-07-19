@echo off
chcp 65001 > nul
title Запуск Версии 1: Консольный REPL (ФП)

:: Автоматическая активация окружения, если оно развернуто
if exist .venv (
    call .venv\Scripts\activate.bat
)

cd version_1_ex7_cli
python app.py
cd ..
