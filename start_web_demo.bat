@echo off
echo Starting YOLO Web Detection Demo...
echo.

echo Installing dependencies...
pip install flask flask-socketio ultralytics opencv-python pillow numpy

echo.
echo Starting Web Server...
echo Open your browser and go to: http://localhost:5000
echo.
python web_app.py

pause
