@echo off
title Farsi HLR
cd /d "%~dp0"
call venv\Scripts\activate.bat
start "" http://localhost:5000
python app.py
pause
