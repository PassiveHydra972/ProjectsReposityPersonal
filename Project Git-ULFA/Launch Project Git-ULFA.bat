@echo off
cd /d "%~dp0"
python main.py
if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] Project Git-ULFA failed to start.
    echo Make sure Python is installed and dependencies are available.
    echo.
    echo Run this to install dependencies:
    echo   pip install -r requirements.txt
    echo.
    pause
)
