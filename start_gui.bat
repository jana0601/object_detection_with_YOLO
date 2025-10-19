@echo off
echo Starting YOLO Real-Time Object Detection GUI...
echo.

echo Installing dependencies...
pip install ultralytics opencv-python pillow numpy

echo.
echo Starting GUI Application...
python gui_app.py

pause
