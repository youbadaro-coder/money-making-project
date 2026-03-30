@echo off
chcp 65001 >nul
set "BASE_DIR=%~dp0"
cd /d "%BASE_DIR%"

echo Starting Shorts Factory V2 Backend (Port 5002)...
:: Add FFmpeg to path
set "PATH=C:\Users\USER\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1-full_build\bin;%PATH%"

start "Shorts Factory V2" cmd /k "python server.py"

echo Waiting for server to start...
timeout /t 3 >nul

echo Opening dashboard...
start http://localhost:5002

echo.
echo ========================================
echo Shorts Factory V2 is now running!
echo Do not close this window while using the app.
echo ========================================
pause
