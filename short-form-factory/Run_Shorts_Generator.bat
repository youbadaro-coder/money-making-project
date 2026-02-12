@echo off
setlocal
cd /d "c:\ai작업\anti\수익화에이전트첫걸음\short-form-factory"

echo --- Shorts Factory Running ---
echo.
echo [1/4] Researching Topic (Annie's Viral Logic)...
"c:\안티작업\.bin\python\python.exe" "c:\ai작업\anti\수익화에이전트첫걸음\short-form-factory\execution\research_topic.py"

echo.
echo [2/4] Fetching Materials (Kodari's Engine)...
"c:\안티작업\.bin\python\python.exe" "c:\ai작업\anti\수익화에이전트첫걸음\short-form-factory\execution\fetch_materials.py"

echo.
echo [3/4] Rendering video (Song's Visual Engine)...
"c:\안티작업\.bin\python\python.exe" "c:\ai작업\anti\수익화에이전트첫걸음\short-form-factory\execution\edit_video.py"

echo.
echo [4/4] Finalizing...
echo (Check .tmp/final_video.mp4)

echo.
echo --- Process Complete! ---
pause
