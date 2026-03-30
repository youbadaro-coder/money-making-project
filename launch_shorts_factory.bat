@echo off
echo ================= Logging started ================= > "C:\Users\USER\Desktop\startup_log.txt"
set "BASE_DIR=%~dp0"
echo [STEP 1] Base directory set to %BASE_DIR% >> "C:\Users\USER\Desktop\startup_log.txt"
cd /d "%BASE_DIR%"

echo [STEP 2] Preparing FFmpeg path... >> "C:\Users\USER\Desktop\startup_log.txt"
set "PATH=C:\Users\USER\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1-full_build\bin;%PATH%"

echo [STEP 3] Starting Python Server... >> "C:\Users\USER\Desktop\startup_log.txt"
start "Shorts Factory V2" cmd /k "python server.py"
if %errorlevel% neq 0 echo Python start failed! Error code: %errorlevel% >> "C:\Users\USER\Desktop\startup_log.txt"

echo [STEP 4] Waiting 3 seconds... >> "C:\Users\USER\Desktop\startup_log.txt"
timeout /t 3 >nul

echo [STEP 5] Opening Dashboard... >> "C:\Users\USER\Desktop\startup_log.txt"
start http://localhost:5002

echo [STEP 6] Batch process complete. >> "C:\Users\USER\Desktop\startup_log.txt"
pause
