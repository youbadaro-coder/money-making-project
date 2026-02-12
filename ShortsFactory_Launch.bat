@echo off
title Shorts Factory Studio Launcher
echo ==========================================
echo   Shorts Factory Studio Launching...
echo ==========================================
echo.

:: Check if server is already running (simple check)
netstat -ano | findstr :5000 > nul
if %errorlevel% equ 0 (
    echo Server is already running. Opening dashboard...
) else (
    echo Starting Backend Server...
    start /b "" "d:\안티작업\.bin\python\python.exe" "d:\안티작업\server.py"
    timeout /t 3 > nul
)

echo Opening Studio Dashboard...
start http://localhost:5000

echo.
echo ==========================================
echo   STAY CRAZY, STAY SHORTS!
echo ==========================================
echo.
pause
