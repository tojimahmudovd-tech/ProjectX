@echo off
setlocal
cd /d %~dp0

echo Creating virtual environment...
python -m venv .venv

echo Activating venv...
call .venv\Scripts\activate

echo Installing requirements...
python -m pip install --upgrade pip
pip install -r requirements.txt

echo Running tests...
python src\api_test_runner.py

echo.
echo Done. Logs saved in reports\
pause
