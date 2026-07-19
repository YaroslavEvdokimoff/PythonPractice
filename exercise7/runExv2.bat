@echo off
chcp 65001 > nul
title Запуск Версии 2: Оконный GUI (ООП + СУБД)

:: Автоматическая активация окружения, если оно развернуто
if exist .venv (
    call .venv\Scripts\activate.bat
)

cd version_2_oop_gui
python app.py
cd ..
