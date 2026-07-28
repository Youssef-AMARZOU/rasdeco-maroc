@echo off
chcp 65001 >nul
setlocal

set "RASD_DIR=%~dp0"
cd /d "%RASD_DIR%"

:: Kill existing RASD processes
taskkill /F /IM electron.exe /FI "WINDOWTITLE eq RASD*" 2>nul

echo Lancement RASD-Maroc...
npx electron electron/main.js
