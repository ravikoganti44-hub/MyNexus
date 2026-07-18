@echo off
REM ProJ Connect - Application Launcher
REM Run the ProJ Connect desktop application

cd /d "%~dp0"

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo Installing dependencies...
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate.bat
)

REM Run the application
echo Starting ProJ Connect...
python src/main.py

pause
