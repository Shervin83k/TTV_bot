@echo off
chcp 65001 >nul
echo Starting Admin Panel...

cd /d "%~dp0"

call venv\Scripts\activate.bat
python src\admin.py

pause