@echo off
title YOLO Object Detection
cd /d "%~dp0"

echo ========================================
echo    YOLO Object Detection Application
echo ========================================
echo.
echo Starting application...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Install dependencies if needed
echo Checking dependencies...
pip install ultralytics opencv-python pillow numpy flask flask-socketio >nul 2>&1

echo.
echo Choose application type:
echo 1. Desktop GUI Application (Recommended)
echo 2. Web Browser Application
echo.
set /p choice="Enter your choice (1 or 2): "

if "%choice%"=="1" (
    echo.
    echo Starting Desktop GUI Application...
    echo Click "Start Camera" then "Start Detection" to begin
    echo.
    python gui_app.py
) else if "%choice%"=="2" (
    echo.
    echo Starting Web Application...
    echo Open your browser and go to: http://localhost:5000
    echo.
    start http://localhost:5000
    python web_app.py
) else (
    echo Invalid choice. Starting Desktop GUI by default...
    python gui_app.py
)

echo.
echo Application closed.
pause
