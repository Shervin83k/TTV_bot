@echo off
chcp 65001 >nul
echo Starting Text-to-Speech Bot...

cd /d "%~dp0"

call venv\Scripts\activate.bat
python src\bot.py

pause
