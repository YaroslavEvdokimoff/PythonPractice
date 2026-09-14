@echo off
:: Принудительно включаем поддержку UTF-8 в консоли Windows
chcp 65001 > nul

echo [BUILD] Installing PyInstaller...
pip install pyinstaller

echo [BUILD] Compiling to autonomous EXE...
pyinstaller --noconsole --onefile --name="Battleship" battleship.py

echo [BUILD] Done! Check the 'dist' folder.
pause
