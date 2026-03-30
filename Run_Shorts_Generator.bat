@echo off
setlocal
cd /d "%~dp0"

echo --- Shorts Factory Running ---
echo.
echo [1/4] Researching Topic (Annie's Viral Logic)...
".bin\python\python.exe" "execution\research_topic.py"

echo.
echo [2/4] Fetching Materials...
".bin\python\python.exe" "execution\fetch_materials.py"

echo.
echo [3/4] Editing Video (Song's Visual Engine)...
".bin\python\python.exe" "execution\edit_video.py"

echo.
echo [4/4] Finalizing...
echo (Check .tmp/final_video.mp4)

echo.
echo --- Process Complete! ---
pause
