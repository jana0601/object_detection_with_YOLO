# PowerShell script to create desktop shortcut for YOLO Detection
$DesktopPath = [Environment]::GetFolderPath("Desktop")
$ShortcutPath = Join-Path $DesktopPath "YOLO Object Detection.lnk"
$TargetPath = Join-Path $PSScriptRoot "YOLO_Detection.bat"
$IconPath = "C:\Windows\System32\imageres.dll,1"  # Camera icon

# Create WScript.Shell object
$WshShell = New-Object -comObject WScript.Shell

# Create shortcut
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $TargetPath
$Shortcut.WorkingDirectory = $PSScriptRoot
$Shortcut.Description = "YOLO Real-Time Object Detection Application"
$Shortcut.IconLocation = $IconPath
$Shortcut.Save()

Write-Host "Desktop shortcut created successfully!" -ForegroundColor Green
Write-Host "Shortcut location: $ShortcutPath" -ForegroundColor Yellow
Write-Host "You can now double-click the shortcut on your desktop to run the application." -ForegroundColor Cyan
