@echo off
echo Starting YOLO Object Detection Application...
echo.

echo Installing Python dependencies...
pip install -r requirements.txt

echo.
echo Installing React dependencies...
cd frontend
npm install

echo.
echo Building React frontend...
npm run build
cd ..

echo.
echo Starting Flask server...
echo Application will be available at: http://localhost:5000
echo.
python app.py

pause
