@echo off
title Hedef AVM Birlesik Yonetim Paneli
cd /d "%~dp0"

set "PY_EXE=C:\Users\HEDEFWOW\AppData\Local\Python\pythoncore-3.14-64\python.exe"
if not exist "%PY_EXE%" set "PY_EXE=python"

echo Hedef AVM Birlesik Yonetim Paneli baslatiliyor...
echo Tarayicida acilacak adres: http://localhost:8509
"%PY_EXE%" -m streamlit run app.py --server.port 8509
pause
