@echo off
title Shorts Factory Studio
cd /d "%~dp0"

echo --- Shorts Factory Studio Server ---
echo.
echo [1/1] Starting Factory Backend (Flask)...
start /b "" ".bin\python\python.exe" "server.py"

echo.
echo [SUCCESS] Studio Dashboard is ready!
echo Launching browser for the Chairman...
timeout /t 3 > nul
start http://localhost:5000

echo.
echo ==========================================
echo  FACTORY SERVER IS ACTIVE IN BACKGROUND
echo  Close this window to stop the server later.
echo ==========================================
echo Running at http://localhost:5000
pause
