@echo off
echo Creating desktop shortcut for YOLO Object Detection...
echo.

REM Run PowerShell script to create shortcut
powershell.exe -ExecutionPolicy Bypass -File "create_shortcut.ps1"

echo.
echo Desktop shortcut creation completed!
echo You should now see "YOLO Object Detection" on your desktop.
echo.
pause
