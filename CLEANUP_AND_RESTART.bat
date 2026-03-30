@echo off
title Shorts Factory Cleanup & Restart
set BASE_DIR=c:\ai작업\anti\수익화에이전트첫걸음\short-form-factory
set ROOT_DIR=c:\ai작업\anti\수익화에이전트첫걸음
set PYTHON_EXE=c:\안티작업\.bin\python\python.exe

echo [1/4] Killing existing Flask server...
taskkill /f /im python.exe /fi "WINDOWTITLE eq Shorts Factory Studio" 2>nul
taskkill /f /im python.exe /fi "COMMANDLINE eq *server.py*" 2>nul

echo [2/4] Cleaning temporary files...
if exist "%BASE_DIR%\.tmp" (
    del /q /s "%BASE_DIR%\.tmp\*.*" >nul 2>&1
)

echo [3/4] Rebuilding launchers...
"%PYTHON_EXE%" "%ROOT_DIR%\rebuild_launchers.py"

echo [4/4] Restarting Studio...
cd /d "%BASE_DIR%"
start /b "" "%PYTHON_EXE%" "%BASE_DIR%\server.py"

echo.
echo ==============================================
echo [SUCCESS] Cleanup complete! 
echo Dashboard should open at http://localhost:5000
echo ==============================================
timeout /t 3 > nul
start http://localhost:5000
pause
