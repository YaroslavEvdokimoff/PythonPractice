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
